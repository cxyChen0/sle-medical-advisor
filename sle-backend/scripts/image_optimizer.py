"""
图片压缩和优化脚本
用于在OCR前对图片进行预处理，提升OCR效率
"""

import os
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image, ImageEnhance, ImageFilter
import time


class ImageOptimizer:
    """图片优化器"""

    def __init__(self, output_dir: str = "optimized_images"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def get_image_info(self, image_path: str) -> dict:
        """获取图片信息"""
        img = Image.open(image_path)
        file_size = os.path.getsize(image_path)
        
        return {
            'path': image_path,
            'format': img.format,
            'mode': img.mode,
            'size': img.size,
            'width': img.width,
            'height': img.height,
            'file_size': file_size,
            'file_size_mb': file_size / (1024 * 1024)
        }

    def resize_image(self, image: Image.Image, max_width: int = 2000, max_height: int = 2000) -> Image.Image:
        """调整图片大小，保持宽高比"""
        width, height = image.size
        
        if width <= max_width and height <= max_height:
            return image
        
        ratio = min(max_width / width, max_height / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def convert_to_grayscale(self, image: Image.Image) -> Image.Image:
        """转换为灰度图"""
        if image.mode != 'L':
            return image.convert('L')
        return image

    def enhance_contrast(self, image: Image.Image, factor: float = 1.5) -> Image.Image:
        """增强对比度"""
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)

    def enhance_sharpness(self, image: Image.Image, factor: float = 1.3) -> Image.Image:
        """增强清晰度"""
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(factor)

    def binarize(self, image: Image.Image, threshold: int = 128) -> Image.Image:
        """二值化处理"""
        if image.mode != 'L':
            image = image.convert('L')
        
        return image.point(lambda x: 0 if x < threshold else 255, '1')

    def denoise(self, image: Image.Image) -> Image.Image:
        """降噪处理"""
        return image.filter(ImageFilter.MedianFilter(size=3))

    def optimize_image(self, 
                      image_path: str, 
                      output_name: Optional[str] = None,
                      resize: bool = True,
                      max_width: int = 2000,
                      max_height: int = 2000,
                      grayscale: bool = True,
                      enhance_contrast: bool = True,
                      enhance_sharpness: bool = True,
                      binarize: bool = False,
                      denoise: bool = False,
                      quality: int = 85,
                      format: str = 'JPEG') -> Tuple[dict, float]:
        """
        优化图片
        
        Args:
            image_path: 原始图片路径
            output_name: 输出文件名（可选）
            resize: 是否调整大小
            max_width: 最大宽度
            max_height: 最大高度
            grayscale: 是否转换为灰度图
            enhance_contrast: 是否增强对比度
            enhance_sharpness: 是否增强清晰度
            binarize: 是否二值化
            denoise: 是否降噪
            quality: JPEG质量（1-100）
            format: 输出格式（JPEG/PNG）
            
        Returns:
            (优化后的图片信息, 处理时间)
        """
        start_time = time.time()
        
        img = Image.open(image_path)
        original_info = self.get_image_info(image_path)
        
        if resize:
            img = self.resize_image(img, max_width, max_height)
        
        if denoise:
            img = self.denoise(img)
        
        if grayscale:
            img = self.convert_to_grayscale(img)
        
        if enhance_contrast:
            img = self.enhance_contrast(img)
        
        if enhance_sharpness:
            img = self.enhance_sharpness(img)
        
        if binarize:
            img = self.binarize(img)
        
        if output_name is None:
            original_name = Path(image_path).stem
            ext = '.jpg' if format == 'JPEG' else '.png'
            output_name = f"{original_name}_optimized{ext}"
        
        output_path = self.output_dir / output_name
        
        if format == 'JPEG':
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
        else:
            img.save(output_path, 'PNG', optimize=True)
        
        processing_time = time.time() - start_time
        optimized_info = self.get_image_info(str(output_path))
        
        return {
            'original': original_info,
            'optimized': optimized_info,
            'output_path': str(output_path)
        }, processing_time


def test_optimization_strategies(image_path: str):
    """测试不同的优化策略"""
    optimizer = ImageOptimizer()
    
    print(f"\n{'='*60}")
    print(f"测试图片: {image_path}")
    print(f"{'='*60}\n")
    
    original_info = optimizer.get_image_info(image_path)
    print(f"原始图片信息:")
    print(f"  尺寸: {original_info['width']}x{original_info['height']}")
    print(f"  文件大小: {original_info['file_size_mb']:.2f} MB")
    print(f"  格式: {original_info['format']}")
    print(f"  模式: {original_info['mode']}")
    
    strategies = [
        {
            'name': '策略1: 仅调整大小',
            'params': {
                'resize': True,
                'max_width': 2000,
                'max_height': 2000,
                'grayscale': False,
                'enhance_contrast': False,
                'enhance_sharpness': False,
                'binarize': False,
                'denoise': False,
                'quality': 85
            }
        },
        {
            'name': '策略2: 调整大小 + 灰度',
            'params': {
                'resize': True,
                'max_width': 2000,
                'max_height': 2000,
                'grayscale': True,
                'enhance_contrast': False,
                'enhance_sharpness': False,
                'binarize': False,
                'denoise': False,
                'quality': 85
            }
        },
        {
            'name': '策略3: 调整大小 + 灰度 + 对比度增强',
            'params': {
                'resize': True,
                'max_width': 2000,
                'max_height': 2000,
                'grayscale': True,
                'enhance_contrast': True,
                'enhance_sharpness': False,
                'binarize': False,
                'denoise': False,
                'quality': 85
            }
        },
        {
            'name': '策略4: 调整大小 + 灰度 + 对比度增强 + 清晰度增强',
            'params': {
                'resize': True,
                'max_width': 2000,
                'max_height': 2000,
                'grayscale': True,
                'enhance_contrast': True,
                'enhance_sharpness': True,
                'binarize': False,
                'denoise': False,
                'quality': 85
            }
        },
        {
            'name': '策略5: 调整大小 + 灰度 + 对比度增强 + 清晰度增强 + 降噪',
            'params': {
                'resize': True,
                'max_width': 2000,
                'max_height': 2000,
                'grayscale': True,
                'enhance_contrast': True,
                'enhance_sharpness': True,
                'binarize': False,
                'denoise': True,
                'quality': 85
            }
        },
        {
            'name': '策略6: 调整大小 + 灰度 + 对比度增强 + 清晰度增强 + 二值化',
            'params': {
                'resize': True,
                'max_width': 2000,
                'max_height': 2000,
                'grayscale': True,
                'enhance_contrast': True,
                'enhance_sharpness': True,
                'binarize': True,
                'denoise': False,
                'quality': 85
            }
        },
        {
            'name': '策略7: 激进压缩 (质量60)',
            'params': {
                'resize': True,
                'max_width': 1500,
                'max_height': 1500,
                'grayscale': True,
                'enhance_contrast': True,
                'enhance_sharpness': True,
                'binarize': False,
                'denoise': False,
                'quality': 60
            }
        }
    ]
    
    results = []
    
    for strategy in strategies:
        print(f"\n{strategy['name']}")
        print("-" * 60)
        
        result, proc_time = optimizer.optimize_image(
            image_path,
            output_name=f"test_{len(results)}.jpg",
            **strategy['params']
        )
        
        original_size = result['original']['file_size_mb']
        optimized_size = result['optimized']['file_size_mb']
        compression_ratio = (1 - optimized_size / original_size) * 100
        
        print(f"  优化后尺寸: {result['optimized']['width']}x{result['optimized']['height']}")
        print(f"  优化后大小: {optimized_size:.2f} MB")
        print(f"  压缩率: {compression_ratio:.1f}%")
        print(f"  处理时间: {proc_time:.3f}秒")
        
        results.append({
            'strategy': strategy['name'],
            'result': result,
            'processing_time': proc_time,
            'compression_ratio': compression_ratio
        })
    
    print(f"\n{'='*60}")
    print("策略对比总结")
    print(f"{'='*60}")
    print(f"{'策略':<40} {'压缩率':<10} {'处理时间':<10}")
    print("-" * 60)
    for r in results:
        print(f"{r['strategy']:<40} {r['compression_ratio']:<10.1f}% {r['processing_time']:<10.3f}s")
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法: python image_optimizer.py <图片路径>")
        print("示例: python image_optimizer.py test_image.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not Path(image_path).exists():
        print(f"错误: 图片文件不存在: {image_path}")
        sys.exit(1)
    
    test_optimization_strategies(image_path)
