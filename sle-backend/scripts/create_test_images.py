"""
生成测试图片脚本
创建包含文本的测试图片，用于OCR性能测试
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path


def create_test_image(output_path: str, text: str, font_size: int = 24, width: int = 800, height: int = 600):
    """
    创建包含文本的测试图片
    
    Args:
        output_path: 输出图片路径
        text: 要写入的文本
        font_size: 字体大小
        width: 图片宽度
        height: 图片高度
    """
    # 创建更高分辨率的图片
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # 优先使用中文字体
    font = None
    font_paths = [
        "C:\Windows\Fonts\msyh.ttf",    # 微软雅黑
        "C:\Windows\Fonts\msyhbd.ttf",  # 微软雅黑粗体
        "C:\Windows\Fonts\simhei.ttf",  # 黑体
        "C:\Windows\Fonts\simsun.ttc",  # 宋体
        "arial.ttf",
    ]
    
    for font_path in font_paths:
        try:
            font = ImageFont.truetype(font_path, font_size)
            print(f"使用字体: {font_path}")
            break
        except Exception as e:
            print(f"尝试字体 {font_path} 失败: {e}")
    
    if font is None:
        font = ImageFont.load_default()
        print("使用默认字体")
    
    lines = text.split('\n')
    y_offset = 50
    
    for line in lines:
        draw.text((50, y_offset), line, fill='black', font=font)
        y_offset += font_size * 1.5
    
    # 保存为PNG格式，无压缩，提高质量
    img.save(output_path, 'PNG', compress_level=0, dpi=(300, 300))
    print(f"测试图片已创建: {output_path}")


def create_medical_report_image():
    """创建医疗报告测试图片"""
    text = """检查单
患者ID: 001
姓名: 张三
性别: 男
年龄: 30
检查日期: 2026-02-11

检查项目: 血常规、生化、免疫

白细胞计数: 5.8 10^9/L
红细胞计数: 4.5 10^12/L
血红蛋白: 145 g/L
血小板计数: 250 10^9/L

抗核抗体: 阳性
抗双链DNA抗体: 120 IU/mL
Sm抗体: 阴性
RNP抗体: 阴性
SSA抗体: 阳性
SSB抗体: 阴性

C3: 0.9 g/L
C4: 0.2 g/L
IgG: 12.0 g/L
IgA: 2.0 g/L
IgM: 1.0 g/L

尿蛋白: 1+
尿红细胞: 阴性
尿白细胞: 阴性"""
    
    output_dir = Path("test_images")
    output_dir.mkdir(exist_ok=True)
    
    create_test_image(
        str(output_dir / "medical_report.png"),
        text,
        font_size=20,
        width=800,
        height=700
    )


def create_large_test_image():
    """创建大尺寸测试图片"""
    text = """这是一个大尺寸的测试图片，用于验证图片压缩对OCR性能的影响。
在实际应用中，医疗检查单可能以高分辨率扫描，导致图片文件很大。
我们需要测试在OCR前对图片进行压缩和优化是否能提升效率。

测试内容包括：
1. 图片压缩率
2. OCR处理时间
3. 识别准确度
4. 文本相似度

通过对比不同优化策略的效果，我们可以找到最佳的预处理方案。

重复文本用于增加图片内容：
白细胞计数: 5.8 10^9/L
红细胞计数: 4.5 10^12/L
血红蛋白: 145 g/L
血小板计数: 250 10^9/L

抗核抗体: 阳性
抗双链DNA抗体: 120 IU/mL
Sm抗体: 阴性
RNP抗体: 阴性
SSA抗体: 阳性
SSB抗体: 阴性

C3: 0.9 g/L
C4: 0.2 g/L
IgG: 12.0 g/L
IgA: 2.0 g/L
IgM: 1.0 g/L

尿蛋白: 1+
尿红细胞: 阴性
尿白细胞: 阴性"""
    
    output_dir = Path("test_images")
    output_dir.mkdir(exist_ok=True)
    
    create_test_image(
        str(output_dir / "large_test.png"),
        text,
        font_size=18,
        width=1200,
        height=1000
    )


def create_various_test_images():
    """创建多种测试图片"""
    output_dir = Path("test_images")
    output_dir.mkdir(exist_ok=True)
    
    test_cases = [
        {
            'name': 'small_text.png',
            'text': '小字体测试\n白细胞: 5.8\n红细胞: 4.5\n血红蛋白: 145',
            'font_size': 12,
            'width': 400,
            'height': 300
        },
        {
            'name': 'medium_text.png',
            'text': '中等字体测试\n白细胞计数: 5.8 10^9/L\n红细胞计数: 4.5 10^12/L\n血红蛋白: 145 g/L\n血小板计数: 250 10^9/L',
            'font_size': 20,
            'width': 600,
            'height': 400
        },
        {
            'name': 'large_text.png',
            'text': '大字体测试\n白细胞计数: 5.8 10^9/L\n红细胞计数: 4.5 10^12/L\n血红蛋白: 145 g/L\n血小板计数: 250 10^9/L',
            'font_size': 32,
            'width': 800,
            'height': 500
        }
    ]
    
    for case in test_cases:
        create_test_image(
            str(output_dir / case['name']),
            case['text'],
            case['font_size'],
            case['width'],
            case['height']
        )


if __name__ == "__main__":
    print("创建测试图片...")
    create_medical_report_image()
    create_large_test_image()
    create_various_test_images()
    print("\n所有测试图片已创建在 test_images/ 目录下")
    print("\n你可以使用以下命令进行OCR性能测试:")
    print("  python scripts/ocr_performance_test.py test_images/medical_report.png")
    print("  python scripts/ocr_performance_test.py test_images/large_test.png all")
