"""
从MySQL数据库读取患者历史病情记录
"""

from db_connector import execute_query
from typing import Dict, List, Optional
import json


def get_patient_by_id(patient_id: int) -> Optional[Dict]:
    """
    根据患者ID获取患者基本信息

    Args:
        patient_id: 患者ID

    Returns:
        患者信息字典,不存在返回None
    """
    query = """
        SELECT patient_id, patient_name, gender, birth_date,
               contact_phone, email, created_at
        FROM patients
        WHERE patient_id = %s
    """
    result = execute_query(query, (patient_id,))
    return result[0] if result else None


def get_patient_by_name(patient_name: str) -> Optional[Dict]:
    """
    根据患者姓名获取患者基本信息

    Args:
        patient_name: 患者姓名

    Returns:
        患者信息字典,不存在返回None
    """
    query = """
        SELECT patient_id, patient_name, gender, birth_date,
               contact_phone, email, created_at
        FROM patients
        WHERE patient_name = %s
    """
    result = execute_query(query, (patient_name,))
    return result[0] if result else None


def get_medical_history(patient_id: int, limit: int = 10) -> List[Dict]:
    """
    获取患者的病史记录

    Args:
        patient_id: 患者ID
        limit: 返回记录数限制

    Returns:
        病史记录列表
    """
    query = """
        SELECT id, patient_id, record_date, diagnosis, symptoms,
               doctor_name, hospital_name, notes
        FROM medical_history
        WHERE patient_id = %s
        ORDER BY record_date DESC
        LIMIT %s
    """
    result = execute_query(query, (patient_id, limit))

    # 解析JSON格式的symptoms字段
    for record in result:
        if record['symptoms']:
            try:
                record['symptoms'] = json.loads(record['symptoms'])
            except json.JSONDecodeError:
                record['symptoms'] = []

    return result if result else []


def get_patient_reports(patient_id: int, report_type: Optional[str] = None,
                       limit: int = 10) -> List[Dict]:
    """
    获取患者的检查单记录

    Args:
        patient_id: 患者ID
        report_type: 报告类型 ('pathology' 或 'lab')
        limit: 返回记录数限制

    Returns:
        检查单记录列表
    """
    query = """
        SELECT report_id, patient_id, report_type, report_date,
               hospital_name, doctor_name, file_path, parsed_data
        FROM medical_reports
        WHERE patient_id = %s
    """
    params = [patient_id]

    if report_type:
        query += " AND report_type = %s"
        params.append(report_type)

    query += " ORDER BY report_date DESC LIMIT %s"
    params.append(limit)

    result = execute_query(query, tuple(params))

    # 解析JSON格式的parsed_data字段
    for record in result:
        if record['parsed_data']:
            try:
                record['parsed_data'] = json.loads(record['parsed_data'])
            except json.JSONDecodeError:
                record['parsed_data'] = {}

    return result if result else []


def get_report_indicators(report_id: int) -> List[Dict]:
    """
    获取指定检查单的所有指标

    Args:
        report_id: 检查单ID

    Returns:
        指标列表
    """
    query = """
        SELECT indicator_id, report_id, indicator_name,
               indicator_value, unit, reference_range,
               is_abnormal, notes
        FROM lab_indicators
        WHERE report_id = %s
        ORDER BY indicator_name
    """
    result = execute_query(query, (report_id,))
    return result if result else []


def get_medications(patient_id: int, active_only: bool = True) -> List[Dict]:
    """
    获取患者的用药记录

    Args:
        patient_id: 患者ID
        active_only: 是否只返回当前正在使用的药

    Returns:
        用药记录列表
    """
    query = """
        SELECT medication_id, patient_id, medication_name,
               dosage, frequency, start_date, end_date, notes
        FROM medications
        WHERE patient_id = %s
    """
    params = [patient_id]

    if active_only:
        query += " AND (end_date IS NULL OR end_date >= CURDATE())"

    query += " ORDER BY start_date DESC"

    result = execute_query(query, tuple(params))
    return result if result else []


def get_consultations(patient_id: int, limit: int = 5) -> List[Dict]:
    """
    获取患者的咨询记录

    Args:
        patient_id: 患者ID
        limit: 返回记录数限制

    Returns:
        咨询记录列表
    """
    query = """
        SELECT consultation_id, patient_id, consultation_date,
               symptoms, questions, advice, follow_up_date
        FROM consultations
        WHERE patient_id = %s
        ORDER BY consultation_date DESC
        LIMIT %s
    """
    result = execute_query(query, (patient_id, limit))

    # 解析JSON格式字段
    for record in result:
        if record['symptoms']:
            try:
                record['symptoms'] = json.loads(record['symptoms'])
            except json.JSONDecodeError:
                record['symptoms'] = []
        if record['questions']:
            try:
                record['questions'] = json.loads(record['questions'])
            except json.JSONDecodeError:
                record['questions'] = []

    return result if result else []


def get_full_patient_history(patient_id: int) -> Dict:
    """
    获取患者的完整历史记录

    Args:
        patient_id: 患者ID

    Returns:
        包含所有历史信息的字典
    """
    # 获取患者基本信息
    patient = get_patient_by_id(patient_id)
    if not patient:
        return {}

    # 获取病史记录
    medical_history = get_medical_history(patient_id)

    # 获取检查单
    pathology_reports = get_patient_reports(patient_id, 'pathology')
    lab_reports = get_patient_reports(patient_id, 'lab')

    # 获取用药记录
    medications = get_medications(patient_id)

    # 获取咨询记录
    consultations = get_consultations(patient_id)

    # 组装完整历史
    full_history = {
        'patient': patient,
        'medical_history': medical_history,
        'pathology_reports': pathology_reports,
        'lab_reports': lab_reports,
        'medications': medications,
        'consultations': consultations
    }

    return full_history


if __name__ == "__main__":
    # 测试代码
    print("测试读取历史记录...")

    # 假设有一个patient_id=1的患者
    patient_id = 1

    # 获取完整历史
    history = get_full_patient_history(patient_id)

    if history:
        print(f"患者姓名: {history['patient']['patient_name']}")
        print(f"病史记录数: {len(history['medical_history'])}")
        print(f"检查单数: {len(history['lab_reports'])}")
        print(f"用药记录数: {len(history['medications'])}")
    else:
        print("未找到该患者的记录")
