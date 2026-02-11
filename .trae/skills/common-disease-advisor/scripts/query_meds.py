"""
查询药品数据库
用于常见病医疗咨询系统的药品推荐
"""

import argparse
import json
import sys
import os

# 添加父目录到路径,以便导入 db_connector
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_connector import execute_query
from typing import Dict, List, Optional


# 简单的药品数据库(示例数据,实际应该从MySQL或文件读取)
MEDICATIONS_DB = {
    'analgesics': [
        {
            'name': '对乙酰氨基酚',
            'generic_name': '对乙酰氨基酚',
            'category': '解热镇痛药',
            'indications': ['发热', '轻至中度疼痛', '头痛', '关节痛', '肌肉痛'],
            'adult_dosage': '每次0.5g,每4-6小时一次,24小时内不超过4次',
            'child_dosage': '每次10-15mg/kg,每4-6小时一次',
            'contraindications': ['严重肝肾功能不全', '对本品过敏者'],
            'precautions': ['长期大量使用可致肝肾功能损害', '避免与其他含对乙酰氨基酚的药品同时使用'],
            'side_effects': ['恶心', '呕吐', '皮疹', '长期过量可致肝损害'],
            'interactions': ['与酒精同用可增加肝毒性', '不宜与氯霉素同用']
        },
        {
            'name': '布洛芬',
            'generic_name': '布洛芬',
            'category': '解热镇痛药',
            'indications': ['发热', '轻至中度疼痛', '头痛', '关节痛', '牙痛', '痛经'],
            'adult_dosage': '每次0.2-0.4g,每4-6小时一次',
            'child_dosage': '每次5-10mg/kg,每6-8小时一次',
            'contraindications': ['对本品过敏者', '活动性消化性溃疡', '严重肝肾功能不全', '孕妇及哺乳期妇女'],
            'precautions': ['饭后服用减少胃肠道刺激', '有消化性溃疡史者慎用', '孕妇禁用'],
            'side_effects': ['胃肠道不适', '恶心', '呕吐', '皮疹', '长期使用可致胃肠道出血'],
            'interactions': ['与阿司匹林同用可降低疗效', '与抗凝药同用可增加出血风险']
        },
        {
            'name': '阿司匹林',
            'generic_name': '阿司匹林',
            'category': '解热镇痛药',
            'indications': ['发热', '轻至中度疼痛', '预防血栓'],
            'adult_dosage': '解热镇痛:每次0.3-0.6g,每日3次',
            'child_dosage': '不推荐儿童使用(可能引起瑞氏综合征)',
            'contraindications': ['对本品过敏者', '活动性消化性溃疡', '出血性疾病', '孕妇', '儿童'],
            'precautions': ['长期使用可致胃肠道出血', '饭后服用', '饮酒前后不宜使用'],
            'side_effects': ['胃肠道不适', '恶心', '呕吐', '耳鸣', '出血倾向'],
            'interactions': ['与华法林同用可增加出血风险', '与糖皮质激素同用可增加胃肠道出血']
        }
    ],
    'cold_meds': [
        {
            'name': '复方氨酚烷胺胶囊',
            'generic_name': '复方氨酚烷胺',
            'category': '感冒用药',
            'indications': ['普通感冒', '流行性感冒', '发热', '头痛', '鼻塞', '流涕', '咳嗽'],
            'adult_dosage': '每次1粒,每日2次',
            'child_dosage': '儿童应在医师指导下使用',
            'contraindications': ['严重肝肾功能不全者', '对本品成分过敏者'],
            'precautions': ['服药期间禁止饮酒', '驾驶车辆及高空作业者慎用', '不宜与其他含对乙酰氨基酚的药品同用'],
            'side_effects': ['轻度嗜睡', '口干', '恶心', '皮疹'],
            'interactions': ['与酒精同用可增加肝毒性', '与中枢抑制药同用可增强抑制作用']
        },
        {
            'name': '酚麻美敏片',
            'generic_name': '酚麻美敏',
            'category': '感冒用药',
            'indications': ['普通感冒', '流行性感冒', '发热', '头痛', '鼻塞', '流涕', '咳嗽'],
            'adult_dosage': '每次1片,每6小时一次,24小时内不超过4次',
            'child_dosage': '6-12岁儿童每次半片,每6小时一次',
            'contraindications': ['对本品成分过敏者', '严重肝肾功能不全者'],
            'precautions': ['服药期间禁止饮酒', '孕妇及哺乳期妇女慎用', '服用本品期间不得驾驶机、车、船'],
            'side_effects': ['轻度嗜睡', '头晕', '恶心', '口干'],
            'interactions': ['与酒精同用可增加中枢抑制作用', '与单胺氧化酶抑制剂同用可致高血压危象']
        }
    ],
    'digestive': [
        {
            'name': '蒙脱石散',
            'generic_name': '蒙脱石',
            'category': '止泻药',
            'indications': ['成人及儿童急慢性腹泻', '食道、胃、十二指肠疾病引起的相关疼痛'],
            'adult_dosage': '每次1袋,每日3次',
            'child_dosage': '1岁以下:每日1袋;1-2岁:每日1-2袋;2岁以上:每日2-3袋,均分3次服用',
            'contraindications': ['对本品过敏者'],
            'precautions': ['急性腹泻需注意脱水,纠正水电解质紊乱', '本品不影响其他药物的吸收', '建议与其他药物间隔1-2小时服用'],
            'side_effects': ['偶见便秘'],
            'interactions': ['建议与其他药物间隔服用']
        },
        {
            'name': '多潘立酮',
            'generic_name': '多潘立酮',
            'category': '促胃动力药',
            'indications': ['消化不良', '腹胀', '嗳气', '恶心', '呕吐'],
            'adult_dosage': '每次10mg,每日3-4次,饭前15-30分钟服用',
            'child_dosage': '儿童应在医师指导下使用',
            'contraindications': ['对本品过敏者', '机械性肠梗阻', '胃肠道出血', '穿孔'],
            'precautions': ['孕妇慎用', '哺乳期妇女慎用', '心脏病患者慎用', '长期使用需定期复查'],
            'side_effects': ['口干', '头痛', '失眠', '腹泻'],
            'interactions': ['与抗胆碱药合用可减弱本品作用', '与酮康唑、红霉素等合用可增加本品的血药浓度']
        },
        {
            'name': '奥美拉唑',
            'generic_name': '奥美拉唑',
            'category': '质子泵抑制剂',
            'indications': ['胃溃疡', '十二指肠溃疡', '反流性食管炎', '胃炎'],
            'adult_dosage': '每次20mg,每日1次,晨起空腹服用',
            'child_dosage': '儿童应在医师指导下使用',
            'contraindications': ['对本品过敏者', '严重肾功能不全者'],
            'precautions': ['长期使用需定期检查肝功能', '孕妇及哺乳期妇女慎用', '老年人慎用'],
            'side_effects': ['头痛', '腹泻', '恶心', '便秘'],
            'interactions': ['与酮康唑、伊曲康唑合用可降低后者吸收', '与华法林合用可延长凝血时间']
        }
    ],
    'antihistamines': [
        {
            'name': '氯雷他定',
            'generic_name': '氯雷他定',
            'category': '抗组胺药',
            'indications': ['过敏性鼻炎', '荨麻疹', '瘙痒性皮肤病'],
            'adult_dosage': '每次10mg,每日1次',
            'child_dosage': '2-12岁儿童:体重>30kg:每次10mg;体重≤30kg:每次5mg',
            'contraindications': ['对本品过敏者'],
            'precautions': ['严重肝功能不全者禁用', '孕妇及哺乳期妇女慎用', '2岁以下儿童慎用'],
            'side_effects': ['嗜睡', '乏力', '头痛', '口干'],
            'interactions': ['与酮康唑、大环内酯类抗生素合用可增加血药浓度']
        },
        {
            'name': '西替利嗪',
            'generic_name': '西替利嗪',
            'category': '抗组胺药',
            'indications': ['过敏性鼻炎', '荨麻疹', '湿疹', '皮炎'],
            'adult_dosage': '每次10mg,每日1次',
            'child_dosage': '6岁以上儿童:每次5-10mg,每日1次;2-6岁儿童:每次2.5-5mg,每日1次',
            'contraindications': ['对本品过敏者'],
            'precautions': ['服药期间避免驾驶及操作机械', '孕妇及哺乳期妇女慎用', '严重肾功能不全者需减量'],
            'side_effects': ['嗜睡', '头晕', '乏力', '口干'],
            'interactions': ['与中枢抑制药同用可增强镇静作用']
        }
    ]
}


def query_medications_by_category(category: str) -> List[Dict]:
    """
    按类别查询药品

    Args:
        category: 药品类别 (analgesics/cold_meds/digestive/antihistamines)

    Returns:
        药品列表
    """
    return MEDICATIONS_DB.get(category, [])


def query_medications_by_symptom(symptom: str) -> List[Dict]:
    """
    按症状查询药品

    Args:
        symptom: 症状描述

    Returns:
        匹配的药品列表
    """
    results = []

    # 症状与药品类别的映射
    symptom_category_map = {
        '发热': ['analgesics', 'cold_meds'],
        '头疼': ['analgesics', 'cold_meds'],
        '头痛': ['analgesics', 'cold_meds'],
        '关节痛': ['analgesics'],
        '肌肉痛': ['analgesics'],
        '牙痛': ['analgesics'],
        '痛经': ['analgesics'],
        '咳嗽': ['cold_meds'],
        '鼻塞': ['cold_meds'],
        '流涕': ['cold_meds'],
        '腹泻': ['digestive'],
        '腹胀': ['digestive'],
        '嗳气': ['digestive'],
        '恶心': ['digestive'],
        '呕吐': ['digestive'],
        '胃痛': ['digestive'],
        '腹痛': ['digestive'],
        '反酸': ['digestive'],
        '烧心': ['digestive'],
        '皮疹': ['antihistamines'],
        '荨麻疹': ['antihistamines'],
        '过敏': ['antihistamines'],
        '瘙痒': ['antihistamines'],
        '鼻痒': ['antihistamines']
    }

    categories = symptom_category_map.get(symptom, [])

    for category in categories:
        meds = query_medications_by_category(category)
        for med in meds:
            if symptom in med['indications']:
                results.append(med)

    return results


def get_medication_details(name: str) -> Optional[Dict]:
    """
    获取药品详细信息

    Args:
        name: 药品名称

    Returns:
        药品详细信息,不存在返回None
    """
    for category, meds in MEDICATIONS_DB.items():
        for med in meds:
            if med['name'] == name or med['generic_name'] == name:
                return med
    return None


def filter_by_contraindications(medications: List[Dict], allergies: List[str],
                              conditions: List[str]) -> List[Dict]:
    """
    根据禁忌症过滤药品

    Args:
        medications: 待筛选的药品列表
        allergies: 过敏史列表
        conditions: 基础疾病列表

    Returns:
        过滤后的药品列表
    """
    filtered = []

    for med in medications:
        # 检查过敏
        has_allergy = any(
            allergy in med['contraindications'] or
            allergy in med.get('precautions', [])
            for allergy in allergies
        )

        # 检查基础疾病
        has_condition_conflict = any(
            condition in med['contraindications']
            for condition in conditions
        )

        if not has_allergy and not has_condition_conflict:
            filtered.append(med)

    return filtered


def recommend_medications(symptom: str, patient_history: Optional[Dict] = None) -> Dict:
    """
    推荐药品

    Args:
        symptom: 症状描述
        patient_history: 患者历史记录(包含过敏史、基础疾病等)

    Returns:
        推荐结果
    """
    # 查询匹配的药品
    medications = query_medications_by_symptom(symptom)

    if not medications:
        return {
            'success': False,
            'message': f'未找到适用于"{symptom}"的药品',
            'medications': []
        }

    # 如果有患者历史,进行过滤
    if patient_history:
        allergies = patient_history.get('allergies', [])
        conditions = patient_history.get('conditions', [])

        if allergies or conditions:
            medications = filter_by_contraindications(medications, allergies, conditions)

    return {
        'success': True,
        'symptom': symptom,
        'medications': medications[:3]  # 最多推荐3个
    }


def print_medication(med: Dict):
    """
    打印药品信息

    Args:
        med: 药品信息字典
    """
    print(f"\n## {med['name']}")
    print(f"**通用名**: {med['generic_name']}")
    print(f"**类别**: {med['category']}")
    print(f"\n**适应症**:")
    for indication in med['indications']:
        print(f"- {indication}")
    print(f"\n**用法用量**:")
    print(f"- 成人: {med.get('adult_dosage', '详见说明书')}")
    print(f"- 儿童: {med.get('child_dosage', '应在医师指导下使用')}")
    print(f"\n**禁忌症**:")
    for contraindication in med.get('contraindications', []):
        print(f"- {contraindication}")
    print(f"\n**注意事项**:")
    for precaution in med.get('precautions', []):
        print(f"- {precaution}")


def main():
    parser = argparse.ArgumentParser(description='查询药品数据库')
    parser.add_argument('--category', type=str,
                       choices=['analgesics', 'cold_meds', 'digestive', 'antihistamines'],
                       help='药品类别')
    parser.add_argument('--symptom', type=str, help='症状')
    parser.add_argument('--name', type=str, help='药品名称')
    parser.add_argument('--output', type=str, help='输出JSON文件路径')

    args = parser.parse_args()

    if args.name:
        # 查询单个药品
        med = get_medication_details(args.name)
        if med:
            print_medication(med)
        else:
            print(f"未找到药品: {args.name}")

    elif args.symptom:
        # 按症状查询
        result = recommend_medications(args.symptom)

        if result['success']:
            print(f"\n适用于'{args.symptom}'的药品:")
            for med in result['medications']:
                print_medication(med)
        else:
            print(result['message'])

    elif args.category:
        # 按类别查询
        medications = query_medications_by_category(args.category)

        print(f"\n{args.category} 类药品:")
        for med in medications:
            print_medication(med)

    else:
        print("错误: 必须指定 --name, --symptom 或 --category 参数")

    # 保存结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result if 'result' in locals() else {}, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到: {args.output}")


if __name__ == '__main__':
    main()
