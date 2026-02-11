"""
图片优化服务
在OCR前对图片进行预处理，提升OCR效率
"""

from pathlib import Path
from typing import Optional
from PIL import Image, ImageEnhance
import os


class ImageOptimizationService:
    """图片优化服务"""

    @staticmethod
    def optimize_for_ocr(image_path: str,
                        max_width: int = 3000,
                        max_height: int = 3000,
                        grayscale: bool = True,
                        enhance_contrast: bool = True,
                        enhance_sharpness: bool = True,
                        quality: int = 95) -> str:
        """
        为OCR优化图片
        
        Args:
            image_path: 原始图片路径
            max_width: 最大宽度
            max_height: 最大高度
            grayscale: 是否转换为灰度图
            enhance_contrast: 是否增强对比度
            enhance_sharpness: 是否增强清晰度
            quality: JPEG质量（1-100）
            
        Returns:
            优化后的图片路径
        """
        img = Image.open(image_path)
        
        img = ImageOptimizationService._resize_image(img, max_width, max_height)
        
        if grayscale:
            img = ImageOptimizationService._convert_to_grayscale(img)
        
        if enhance_contrast:
            img = ImageOptimizationService._enhance_contrast(img, factor=1.5)
        
        if enhance_sharpness:
            img = ImageOptimizationService._enhance_sharpness(img, factor=1.3)
        
        output_path = str(Path(image_path).with_suffix('.optimized.jpg'))
        img.save(output_path, 'JPEG', quality=quality, optimize=True)
        
        return output_path
    
    @staticmethod
    def _denoise_image(image: Image.Image) -> Image.Image:
        """简单的去噪处理 - 使用中值滤波"""
        try:
            import numpy as np
            from PIL import ImageFilter
            
            if image.mode != 'L':
                image = image.convert('L')
            
            img_array = np.array(image)
            from scipy.ndimage import median_filter
            img_array = median_filter(img_array, size=3)
            
            return Image.fromarray(img_array)
        except ImportError:
            return image

    @staticmethod
    def _resize_image(image: Image.Image, max_width: int, max_height: int) -> Image.Image:
        """调整图片大小，保持宽高比"""
        width, height = image.size
        
        if width <= max_width and height <= max_height:
            return image
        
        ratio = min(max_width / width, max_height / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    @staticmethod
    def _convert_to_grayscale(image: Image.Image) -> Image.Image:
        """转换为灰度图"""
        if image.mode != 'L':
            return image.convert('L')
        return image

    @staticmethod
    def _enhance_contrast(image: Image.Image, factor: float = 1.5) -> Image.Image:
        """增强对比度"""
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)

    @staticmethod
    def _enhance_sharpness(image: Image.Image, factor: float = 1.3) -> Image.Image:
        """增强清晰度"""
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(factor)


image_optimization_service = ImageOptimizationService()
