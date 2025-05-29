# engine/analyzer.py
import json
import os
import sys
import base64
from typing import Dict, Any, Optional
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# Import from project modules
from engine.processors.image_processor import ImageProcessor
from engine.validators.output_validator import OutputValidator
from shared.config import Config
from shared.schemas import AnalysisResult, TyphoonSafetyAssessment

class TyphoonSafetyAnalyzer:
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.config = Config()
        
        # Use config values for LLM initialization
        self.llm = ChatGoogleGenerativeAI(
            model=self.config.default_model,
            temperature=self.config.temperature,
            max_output_tokens=self.config.max_tokens,  # Gemini uses max_output_tokens
            google_api_key=self.config.google_api_key
        )
        self.image_processor = ImageProcessor()
        self.validator = OutputValidator()
        
        # Load sample data if in debug mode
        if self.debug:
            self.sample_data_path = Path(__file__).parent / "sample_data"
            self._load_sample_images()
    
    def _load_sample_images(self):
        """Load sample images for debugging"""
        self.sample_images = []
        if self.sample_data_path.exists():
            for img_file in self.sample_data_path.glob("*.{jpg,jpeg,png,bmp}"):
                self.sample_images.append(str(img_file))
            print(f"Loaded {len(self.sample_images)} sample images for debugging")
    
    def analyze_image(self, image_path: str, guidelines: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze image for typhoon safety hazards
        
        Args:
            image_path: Path to the image file
            guidelines: Optional specific guidelines for analysis
            
        Returns:
            JSON analysis result
        """
        try:
            # Process image
            processed_image = self.image_processor.process_image(image_path)
            
            if not processed_image['success']:
                raise Exception(f"Image processing failed: {processed_image.get('error')}")
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(guidelines)
            
            # Use processed image path
            processed_path = processed_image['processed_path']
            image_base64 = self._encode_image_to_base64(processed_path)
            
            # Create message with image
            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            )
            
            # Get analysis from LLM
            response = self.llm.invoke([message])
            
            # Parse and validate response
            analysis_result = self._parse_response(response.content)
            validated_result = self.validator.validate(analysis_result)
            
            if self.debug:
                print(f"Analysis completed for: {os.path.basename(image_path)}")
                print(f"Result: {json.dumps(validated_result, indent=2)}")
            
            return validated_result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "image_path": image_path,
                "timestamp": self.config.get_current_timestamp()
            }
            if self.debug:
                print(f"Error analyzing {image_path}: {str(e)}")
            return error_result
    
    def analyze_sample_images(self) -> Dict[str, Any]:
        """Analyze all sample images (debug mode only)"""
        if not self.debug:
            return {"error": "Sample analysis only available in debug mode"}
        
        results = []
        for img_path in self.sample_images:
            result = self.analyze_image(img_path)
            results.append({
                "image_name": os.path.basename(img_path),
                "analysis": result
            })
        
        return {
            "total_images": len(self.sample_images),
            "results": results,
            "timestamp": self.config.get_current_timestamp()
        }
    
    def _create_analysis_prompt(self, guidelines: Optional[str] = None) -> str:
        """Create the analysis prompt for typhoon safety assessment"""
        base_prompt = """
        태풍이 올 때 위험할 수 있는 물건이나 결함을 사진에서 분석해주세요.
        
        다음 카테고리별로 위험요소를 확인하고 각각의 위험도를 평가해주세요:

        ## 1. 날아갈 수 있는 물건들 (Flying Objects)
        **쉽게 날아가는 것들:** 쓰레기, 비닐봉지, 종이류, 가벼운 화분, 플라스틱 의자, 현수막, 천막, 파라솔, 임시 간판
        **무거워서 잘 안 날아가지만 위험한 것들:** 철제 표지판, 간판, 건설장비, 철근, 자재, 에어컨 실외기, 대형 화분, 석재

        ## 2. 구조적 취약점 (Structural Vulnerabilities)  
        깨진/금간 창문, 느슨한 간판, 옥외광고, 손상된 지붕재, 기와, 불안정한 임시구조물, 녹슨 난간, 울타리

        ## 3. 높은 곳의 위험물 (Elevated Objects)
        난간 위 화분, 베란다 빨래건조대, 옥상 물건들 (물탱크, 안테나 등)

        ## 4. 나무 관련 (Tree Hazards) - 명확히 보이는 것만
        명확히 기울어진 나무, 이미 부러진 가지들, 잎이 말라 죽은 나무, 건물에 너무 가까운 큰 나무

        ## 위험도 평가 기준:
        - **이동 용이성**: high(쉽게 날아감) / medium(어느정도) / low(잘 안움직임)
        - **충격 위험도**: critical(사망위험) / high(중상) / medium(경상) / low(거의 무해)
        - **종합 위험도**: critical / high / medium / low

        분석 결과는 다음 JSON 형식으로 반환해주세요:
        {
            "overall_risk_level": "low|medium|high|critical",
            "hazards_by_category": {
                "flying_objects": [
                    {
                        "item": "구체적인 물건명",
                        "description": "상세 설명",
                        "movement_risk": "high|medium|low",
                        "impact_severity": "critical|high|medium|low",
                        "overall_risk": "critical|high|medium|low",
                        "location": "이미지에서의 구체적 위치",
                        "recommendation": "권장 조치"
                    }
                ],
                "structural_damage": [
                    {
                        "item": "구조물명",
                        "description": "손상 상태",
                        "risk_level": "critical|high|medium|low",
                        "location": "위치",
                        "recommendation": "권장 조치"
                    }
                ],
                "elevated_objects": [
                    {
                        "item": "물건명",
                        "description": "상태",
                        "fall_risk": "high|medium|low",
                        "impact_severity": "critical|high|medium|low",
                        "overall_risk": "critical|high|medium|low",
                        "location": "위치",
                        "recommendation": "권장 조치"
                    }
                ],
                "tree_hazards": [
                    {
                        "description": "나무 상태",
                        "risk_level": "critical|high|medium|low",
                        "location": "위치",
                        "recommendation": "권장 조치"
                    }
                ]
            },
            "risk_summary": {
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
                "total_hazards": 0
            },
            "urgent_actions": ["즉시 필요한 조치들"],
            "summary": "전반적인 평가",
            "confidence_score": 0.85
        }
        """
        
        if guidelines:
            base_prompt += f"\n\n추가 가이드라인:\n{guidelines}"
        
        return base_prompt
    
    def _encode_image_to_base64(self, image_path: str) -> str:
        """Encode image to base64 string"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response to extract JSON"""
        try:
            # Try to extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback if no JSON found
                return {
                    "overall_risk_level": "unknown",
                    "hazards_detected": [],
                    "summary": response_text,
                    "urgent_actions": [],
                    "confidence_score": 0.0,
                    "raw_response": response_text
                }
        except json.JSONDecodeError:
            return {
                "overall_risk_level": "unknown",
                "hazards_detected": [],
                "summary": "Failed to parse response",
                "urgent_actions": [],
                "confidence_score": 0.0,
                "raw_response": response_text
            }


# Debug runner
if __name__ == "__main__":
    analyzer = TyphoonSafetyAnalyzer(debug=True)
    
    # Test with sample images
    print("=== Typhoon Safety Analyzer - Debug Mode ===")
    results = analyzer.analyze_sample_images()
    print(json.dumps(results, indent=2))