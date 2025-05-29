# engine/processors/image_processor.py
from PIL import Image
import os
from typing import Tuple, Optional

class ImageProcessor:
    def __init__(self, max_size: Tuple[int, int] = (1024, 1024)):
        self.max_size = max_size
    
    def process_image(self, image_path: str) -> dict:
        """
        Process image for analysis - resize, validate, extract metadata
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dict with processed image info
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        try:
            with Image.open(image_path) as img:
                # Get original dimensions
                original_size = img.size
                
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if too large
                if img.size[0] > self.max_size[0] or img.size[1] > self.max_size[1]:
                    img.thumbnail(self.max_size, Image.Resampling.LANCZOS)
                
                # Extract metadata
                metadata = {
                    'original_size': original_size,
                    'processed_size': img.size,
                    'format': img.format,
                    'mode': img.mode,
                    'file_size': os.path.getsize(image_path)
                }
                
                return {
                    'success': True,
                    'metadata': metadata,
                    'processed_path': image_path  # In real implementation, might save processed version
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'image_path': image_path
            }