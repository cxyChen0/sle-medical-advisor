"""
从MySQL数据库读取患者历史记录
与SLE Skill共用同一个数据库
"""

import sys
import os

# 添加SLE Skill的scripts目录到路径
sle_skill_path = "D:\\opencode\\.opencode\\skills\\sle-medical-advisor\\scripts"
sys.path.insert(0, sle_skill_path)

try:
    from load_history import (
        get_patient_by_id,
        get_patient_by_name,
        get_medical_history,
        get_medications,
        get_consultations,
        get_full_patient_history
    )
    print("成功加载历史记录读取模块(来自SLE Skill)")
except ImportError as e:
    print(f"警告: 无法加载SLE Skill的模块: {e}")
    print("请确保SLE Medical Advisor Skill已正确安装")
    sys.exit(1)


def get_allergies(patient_id: int):
    """
    获取患者的过敏记录

    Args:
        patient_id: 患者ID

    Returns:
        过敏记录列表
    """
    try:
        from db_connector import execute_query
        import json

        query = """
            SELECT allergy_id, patient_id, allergen_type, allergen_name,
                   severity, symptoms, diagnosed_date
            FROM allergies
            WHERE patient_id = %s
            ORDER BY diagnosed_date DESC
        """
        result = execute_query(query, (patient_id,))

        # 解析症状
        allergies = result if result else []
        for allergy in allergies:
            if allergy.get('symptoms'):
                try:
                    allergy['symptoms'] = json.loads(allergy['symptoms'])
                except json.JSONDecodeError:
                    allergy['symptoms'] = []

        return allergies

    except Exception as e:
        print(f"获取过敏记录错误: {e}")
        return []


def get_patient_history_for_advisor(patient_id: int):
    """
    获取患者用于常见病咨询的完整历史记录

    Args:
        patient_id: 患者ID

    Returns:
        包含所有相关信息的字典
    """
    # 获取基本信息
    patient = get_patient_by_id(patient_id)

    if not patient:
        return {}

    # 获取病史记录
    medical_history = get_medical_history(patient_id)

    # 获取用药记录
    medications = get_medications(patient_id)

    # 获取过敏记录
    allergies = get_allergies(patient_id)

    # 获取咨询记录
    consultations = get_consultations(patient_id)

    # 提取基础疾病
    conditions = []
    for history in medical_history:
        diagnosis = history.get('diagnosis')
        if diagnosis and diagnosis not in conditions:
            conditions.append(diagnosis)

    # 提取过敏原
    allergens = [a['allergen_name'] for a in allergies]

    # 组装返回数据
    return {
        'patient': patient,
        'medical_history': medical_history,
        'medications': medications,
        'allergies': allergies,
        'consultations': consultations,
        'conditions': conditions,
        'allergen_list': allergens
    }


if __name__ == "__main__":
    # 测试代码
    print("测试读取历史记录...")

    # 假设有一个patient_id=1的患者
    patient_id = 1

    # 获取完整历史
    history = get_patient_history_for_advisor(patient_id)

    if history:
        print(f"患者姓名: {history['patient']['patient_name']}")
        print(f"病史记录数: {len(history['medical_history'])}")
        print(f"用药记录数: {len(history['medications'])}")
        print(f"过敏记录数: {len(history['allergies'])}")
        print(f"基础疾病: {', '.join(history['conditions'])}")
        print(f"过敏原: {', '.join(history['allergen_list'])}")
    else:
        print("未找到该患者的记录")
