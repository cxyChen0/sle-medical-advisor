"""
AI语义分类功能验证测试
用于验证AI兜底方案是否正常工作
"""

import asyncio
from app.services.normalization_service import normalize_medical_terms
from app.services.ai_semantic_service import classify_term_with_ai
from app.config.settings import settings


async def test_known_terms():
    """测试已知术语（应该使用传统方法，不触发AI）"""
    print("=== 测试已知术语（传统归一化） ===\n")
    
    known_terms = [
        "ANA",           # 精确匹配
        "白细胞",        # 精确匹配
        "尿蛋白",        # 精确匹配
        "补体C3",        # 精确匹配
        "抗dsDNA抗体",   # 精确匹配
        "血红蛋白浓度",  # 部分匹配
        "血小板数",      # 部分匹配
        "免疫球蛋白G"    # 部分匹配
    ]
    
    results = await normalize_medical_terms(known_terms)
    
    print(f"{'原始术语':<20} {'归一化结果':<20} {'置信度':<10} {'方法'}")
    print("-" * 70)
    
    for result in results:
        method = "精确匹配" if result['confidence'] == 1.0 else \
                 "部分匹配" if result['confidence'] == 0.8 else \
                 "关键词匹配" if result['confidence'] == 0.6 else "AI分类"
        
        print(f"{result['original']:<20} {result['normalized']:<20} "
              f"{result['confidence']:<10.2f} {method}")
    
    print()


async def test_unknown_terms():
    """测试未知术语（应该触发AI兜底）"""
    print("=== 测试未知术语（AI兜底） ===\n")
    
    unknown_terms = [
        "抗Ro抗体",       # 未知变体
        "抗La抗体",       # 未知变体
        "白细胞数量",     # 未知变体
        "尿液蛋白质",     # 未知变体
        "补体成分3",      # 未知变体
        "免疫球蛋白M",    # 未知变体
        "完全未知术语",   # 完全未知
        "患者姓名",       # 常见字段
        "联系电话"        # 常见字段
    ]
    
    results = await normalize_medical_terms(unknown_terms)
    
    print(f"{'原始术语':<20} {'归一化结果':<20} {'置信度':<10} {'方法'}")
    print("-" * 70)
    
    for result in results:
        method = "精确匹配" if result['confidence'] == 1.0 else \
                 "部分匹配" if result['confidence'] == 0.8 else \
                 "关键词匹配" if result['confidence'] == 0.6 else \
                 "常见字段" if result['confidence'] >= 0.8 else "AI分类"
        
        print(f"{result['original']:<20} {result['normalized']:<20} "
              f"{result['confidence']:<10.2f} {method}")
    
    print()


async def test_ai_directly():
    """直接测试AI分类功能"""
    print("=== 直接测试AI分类功能 ===\n")
    
    test_terms = [
        "抗Ro抗体",
        "抗La抗体",
        "白细胞数量",
        "完全未知术语"
    ]
    
    for term in test_terms:
        result = await classify_term_with_ai(term)
        print(f"原始术语: {term}")
        print(f"归一化: {result['normalized']}")
        print(f"类别: {result['category']}")
        print(f"置信度: {result['confidence']:.2f}")
        print(f"说明: {result['explanation']}")
        print(f"是否使用AI结果: {'是' if result['confidence'] >= settings.AI_NORMALIZATION_THRESHOLD else '否'}")
        print("-" * 50)
    
    print()


async def test_threshold_behavior():
    """测试阈值行为"""
    print("=== 测试阈值行为 ===\n")
    
    threshold = settings.AI_NORMALIZATION_THRESHOLD
    print(f"当前AI归一化阈值: {threshold}")
    print()
    
    test_term = "抗Ro抗体"
    
    print(f"测试术语: {test_term}")
    result = await classify_term_with_ai(test_term)
    
    print(f"AI返回置信度: {result['confidence']:.2f}")
    print(f"阈值: {threshold:.2f}")
    
    if result['confidence'] >= threshold:
        print(f"✅ 置信度 >= 阈值，使用AI归一化结果: {result['normalized']}")
    else:
        print(f"❌ 置信度 < 阈值，使用原术语: {test_term}")
    
    print()


async def test_mixed_terms():
    """测试混合术语（已知+未知）"""
    print("=== 测试混合术语 ===\n")
    
    mixed_terms = [
        "ANA",           # 已知
        "抗Ro抗体",      # 未知
        "白细胞",        # 已知
        "尿液蛋白质",     # 未知
        "补体C3",        # 已知
        "免疫球蛋白M",   # 未知
        "患者姓名",      # 常见字段
        "血红蛋白浓度"   # 已知变体
    ]
    
    results = await normalize_medical_terms(mixed_terms)
    
    print(f"{'原始术语':<20} {'归一化结果':<20} {'置信度':<10} {'方法'}")
    print("-" * 70)
    
    for result in results:
        conf = result['confidence']
        method = "精确匹配" if conf == 1.0 else \
                 "部分匹配" if conf == 0.8 else \
                 "关键词匹配" if conf == 0.6 else \
                 "常见字段" if conf >= 0.8 and result['normalized'] == result['original'] else "AI分类"
        
        print(f"{result['original']:<20} {result['normalized']:<20} "
              f"{conf:<10.2f} {method}")
    
    print()


async def test_api_configuration():
    """测试API配置"""
    print("=== API配置检查 ===\n")
    
    print(f"AI服务提供商: {settings.AI_SERVICE_PROVIDER}")
    print(f"AI归一化阈值: {settings.AI_NORMALIZATION_THRESHOLD}")
    print(f"阿里云API密钥: {'已配置' if settings.ALIYUN_API_KEY and settings.ALIYUN_API_KEY != 'your_aliyun_api_key_here' else '未配置'}")
    print(f"阿里云模型: {settings.ALIYUN_MODEL}")
    print(f"智谱API密钥: {'已配置' if settings.ZHIPU_API_KEY and settings.ZHIPU_API_KEY != 'your_zhipu_api_key_here' else '未配置'}")
    print(f"智谱模型: {settings.ZHIPU_MODEL}")
    print()


async def main():
    """主测试函数"""
    print("=" * 70)
    print("AI语义分类功能验证测试")
    print("=" * 70)
    print()
    
    try:
        await test_api_configuration()
        await test_known_terms()
        await test_unknown_terms()
        await test_ai_directly()
        await test_threshold_behavior()
        await test_mixed_terms()
        
        print("=" * 70)
        print("✅ 所有验证测试完成！")
        print("=" * 70)
        print()
        print("验证要点：")
        print("1. 已知术语应该使用传统方法（置信度 >= 0.6）")
        print("2. 未知术语应该触发AI分类（如果AI置信度 >= 阈值）")
        print("3. AI分类置信度低于阈值时，应返回原术语（置信度 0.5）")
        print("4. 常见字段名应该被正确识别（置信度 >= 0.8）")
        
    except Exception as e:
        print(f"\n❌ 验证测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())