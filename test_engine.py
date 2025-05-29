"""
Test script for the typhoon safety analyzer engine
Run this after setting up the project structure and adding sample images
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def main():
    print("=== Typhoon Safety Analyzer Test ===")
    
    # Check .env file
    env_path = project_root / ".env"
    if not env_path.exists():
        print("❌ .env file not found!")
        print("Please create .env file in project root with:")
        print("GEMINI_API_KEY=your_api_key_here")
        print("DEBUG=true")
        return
    
    # Import after checking .env
    try:
        from engine.analyzer import TyphoonSafetyAnalyzer
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("Please check your .env file and ensure GEMINI_API_KEY is set")
        return
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return
    
    # Check if sample images exist
    sample_path = project_root / "engine" / "sample_data"
    if not sample_path.exists():
        print(f"Creating sample_data directory: {sample_path}")
        sample_path.mkdir(parents=True, exist_ok=True)
        print("📁 Please add some sample images to engine/sample_data/ folder")
        print("Supported formats: .jpg, .jpeg, .png, .bmp")
        return
    
    # Check for images
    image_files = list(sample_path.glob("*.jpg")) + list(sample_path.glob("*.jpeg")) + \
                  list(sample_path.glob("*.png")) + list(sample_path.glob("*.bmp"))
    
    if not image_files:
        print("📷 No sample images found in engine/sample_data/")
        print("Please add some sample images to test the analyzer")
        return
    
    print(f"✅ Found {len(image_files)} sample images")
    
    # Initialize analyzer in debug mode
    try:
        analyzer = TyphoonSafetyAnalyzer(debug=True)
        print("✅ Analyzer initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize analyzer: {e}")
        return
    
    # Test individual image analysis
    print("\n=== Testing Individual Image Analysis ===")
    first_image = str(image_files[0])
    try:
        result = analyzer.analyze_image(first_image)
        print(f"📊 Analysis result for {os.path.basename(first_image)}:")
        print(f"   Risk Level: {result.get('overall_risk_level', 'unknown')}")
        
        # Count hazards
        hazards_by_category = result.get('hazards_by_category', {})
        total_hazards = sum(len(hazards) for hazards in hazards_by_category.values())
        print(f"   Total Hazards Found: {total_hazards}")
        
        for category, hazards in hazards_by_category.items():
            if hazards:
                print(f"   - {category}: {len(hazards)} items")
        
    except Exception as e:
        print(f"❌ Error analyzing individual image: {e}")
    
    # Test batch analysis
    print("\n=== Testing Batch Analysis ===")
    try:
        batch_results = analyzer.analyze_sample_images()
        print(f"📈 Processed {batch_results.get('total_images', 0)} images")
        
        # Summary of all results
        all_risk_levels = []
        for result in batch_results.get('results', []):
            analysis = result.get('analysis', {})
            risk_level = analysis.get('overall_risk_level', 'unknown')
            all_risk_levels.append(risk_level)
        
        if all_risk_levels:
            print(f"   Risk level distribution:")
            for level in ['critical', 'high', 'medium', 'low']:
                count = all_risk_levels.count(level)
                if count > 0:
                    print(f"   - {level}: {count} images")
        
    except Exception as e:
        print(f"❌ Error in batch analysis: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()