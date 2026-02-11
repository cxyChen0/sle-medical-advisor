"""
患者病史服务
用于获取患者的历史病情记录
"""

from typing import Dict, List, Optional
import json
import os

# 模拟数据库连接和查询
# 实际项目中会使用真实的数据库连接

# 模拟患者数据
MOCK_PATIENT_DATA = {
    "1": {
        "patient_id": "1",
        "medical_history": [
            {
                "date": "2026-01-15",
                "diagnosis": "系统性红斑狼疮",
                "symptoms": ["关节疼痛", "面部红斑", "疲劳"],
                "lab_results": {
                    "抗核抗体": "阳性",
                    "抗双链DNA抗体": "阳性",
                    "C3": "0.7",
                    "白细胞计数": "3.8"
                },
                "medications": ["泼尼松", "羟氯喹"]
            },
            {
                "date": "2025-12-10",
                "diagnosis": "系统性红斑狼疮",
                "symptoms": ["关节疼痛", "疲劳"],
                "lab_results": {
                    "抗核抗体": "阳性",
                    "抗双链DNA抗体": "弱阳性",
                    "C3": "0.8",
                    "白细胞计数": "4.2"
                },
                "medications": ["泼尼松", "羟氯喹"]
            }
        ]
    },
    "2": {
        "patient_id": "2",
        "medical_history": [
            {
                "date": "2026-01-20",
                "diagnosis": "系统性红斑狼疮",
                "symptoms": ["面部红斑", "脱发", "口腔溃疡"],
                "lab_results": {
                    "抗核抗体": "阳性",
                    "抗双链DNA抗体": "阳性",
                    "C3": "0.6",
                    "C4": "0.1"
                },
                "medications": ["泼尼松", "羟氯喹", "环磷酰胺"]
            }
        ]
    }
}


async def get_medical_history(patient_id: str) -> Dict:
    """
    获取患者的病史记录
    
    Args:
        patient_id: 患者ID
        
    Returns:
        病史记录字典
    """
    try:
        # 模拟从数据库获取数据
        # 实际项目中会调用真实的数据库查询
        if patient_id in MOCK_PATIENT_DATA:
            return MOCK_PATIENT_DATA[patient_id]
        else:
            # 患者不存在，返回空数据
            return {
                "patient_id": patient_id,
                "medical_history": []
            }
    except Exception as e:
        print(f"获取病史记录时出错: {e}")
        # 出错时返回空数据
        return {
            "patient_id": patient_id,
            "medical_history": []
        }


async def get_full_patient_history(patient_id: str) -> Dict:
    """
    获取患者的完整历史记录
    
    Args:
        patient_id: 患者ID
        
    Returns:
        包含所有历史信息的字典
    """
    try:
        # 模拟从数据库获取完整数据
        # 实际项目中会调用真实的数据库查询
        if patient_id in MOCK_PATIENT_DATA:
            base_data = MOCK_PATIENT_DATA[patient_id]
            # 模拟添加更多数据
            full_data = {
                **base_data,
                "patient_info": {
                    "patient_id": patient_id,
                    "name": f"患者{patient_id}",
                    "gender": "女",
                    "age": 35
                },
                "medications": ["泼尼松", "羟氯喹"],
                "consultations": [
                    {
                        "date": "2026-01-15",
                        "symptoms": ["关节疼痛", "面部红斑"],
                        "advice": "继续当前治疗方案，注意休息"
                    }
                ]
            }
            return full_data
        else:
            # 患者不存在，返回空数据
            return {
                "patient_id": patient_id,
                "medical_history": [],
                "patient_info": {},
                "medications": [],
                "consultations": []
            }
    except Exception as e:
        print(f"获取完整病史记录时出错: {e}")
        # 出错时返回空数据
        return {
            "patient_id": patient_id,
            "medical_history": [],
            "patient_info": {},
            "medications": [],
            "consultations": []
        }
