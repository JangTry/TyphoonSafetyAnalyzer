# shared/config.py
import os
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path

class Config:
    def __init__(self):
        # Load .env file from project root
        project_root = Path(__file__).parent.parent
        env_path = project_root / '.env'
        load_dotenv(env_path)
        
        # Google API Key
        self.google_api_key = os.getenv('GEMINI_API_KEY')
        
        # Model settings
        self.default_model = os.getenv('DEFAULT_MODEL', 'gemini-1.5-flash')
        self.max_tokens = int(os.getenv('MAX_TOKENS', '1000'))
        self.temperature = float(os.getenv('TEMPERATURE', '0.1'))
        
        # Image processing
        self.max_image_size = (1024, 1024)
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp']
        
        # Debug settings
        self.debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
        
        # Validate required settings
        if not self.google_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    def get_current_timestamp(self) -> str:
        return datetime.now().isoformat()


# shared/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class HazardDetection(BaseModel):
    type: str = Field(..., description="Category of the hazard")
    description: str = Field(..., description="Detailed description of the hazard")
    risk_level: str = Field(..., description="Risk level: low, medium, high, critical")
    location: str = Field(..., description="Location of hazard in the image")
    recommendation: str = Field(..., description="Recommended action to take")

class TyphoonSafetyAssessment(BaseModel):
    overall_risk_level: str = Field(..., description="Overall risk assessment")
    hazards_detected: List[HazardDetection] = Field(default_factory=list)
    summary: str = Field(..., description="Brief overall assessment")
    urgent_actions: List[str] = Field(default_factory=list)
    confidence_score: float = Field(..., ge=0.0, le=1.0)

class AnalysisResult(BaseModel):
    success: bool
    result: Optional[TyphoonSafetyAssessment] = None
    error: Optional[str] = None
    image_path: str
    timestamp: datetime
    processing_time: Optional[float] = None