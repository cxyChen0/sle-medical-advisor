"""
测试AI语义分类服务
"""

import asyncio
from app.services.ai_semantic_service import classify_term_with_ai, classify_terms_batch_with_ai


async def test_single_term():
    """测试单个术语分类"""
    print("=== 测试单个术语分类 ===\n")
    
    test_terms = [
        "ANA",
        "白细胞",
        "尿蛋白",
        "补体C3",
        "抗dsDNA抗体",
        "血红蛋白浓度",
        "血小板数",
        "免疫球蛋白G",
        "未知术语测试",
        "抗Ro抗体"
    ]
    
    for term in test_terms:
        result = await classify_term_with_ai(term)
        print(f"原始术语: {term}")
        print(f"归一化: {result['normalized']}")
        print(f"类别: {result['category']}")
        print(f"置信度: {result['confidence']:.2f}")
        print(f"说明: {result['explanation']}")
        print("-" * 50)


async def test_batch_terms():
    """测试批量术语分类"""
    print("\n=== 测试批量术语分类 ===\n")
    
    test_terms = [
        "ANA",
        "白细胞",
        "尿蛋白",
        "补体C3",
        "抗dsDNA抗体",
        "血红蛋白浓度",
        "血小板数",
        "免疫球蛋白G"
    ]
    
    results = await classify_terms_batch_with_ai(test_terms)
    
    for result in results:
        print(f"{result['normalized']:<20} (置信度: {result['confidence']:.2f}) - {result['category']}")


async def test_normalization_integration():
    """测试与归一化服务的集成"""
    print("\n=== 测试归一化服务集成 ===\n")
    
    from app.services.normalization_service import normalize_medical_terms
    
    test_terms = [
        "ANA",
        "白细胞",
        "尿蛋白",
        "补体C3",
        "抗dsDNA抗体",
        "血红蛋白浓度",
        "血小板数",
        "免疫球蛋白G",
        "未知术语测试"
    ]
    
    results = await normalize_medical_terms(test_terms)
    
    for result in results:
        print(f"{result['original']:<20} → {result['normalized']:<20} (置信度: {result['confidence']:.2f})")


async def main():
    """主测试函数"""
    print("开始测试AI语义分类服务...\n")
    
    try:
        await test_single_term()
        await test_batch_terms()
        await test_normalization_integration()
        
        print("\n✅ 所有测试完成！")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())