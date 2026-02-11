"""
构建SLE知识图谱
基于患者的历史数据、检查结果和症状信息
"""

import json
from typing import Dict, List, Optional
from datetime import datetime


def build_knowledge_node(node_type: str, name: str, data: Dict) -> Dict:
    """
    创建知识图谱节点

    Args:
        node_type: 节点类型 (patient/disease/symptom/indicator/treatment)
        name: 节点名称
        data: 节点数据

    Returns:
        节点字典
    """
    return {
        'type': node_type,
        'name': name,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }


def build_knowledge_edge(source: str, target: str, relation: str,
                         weight: float = 1.0, data: Optional[Dict] = None) -> Dict:
    """
    创建知识图谱边

    Args:
        source: 源节点ID
        target: 目标节点ID
        relation: 关系类型
        weight: 关系权重
        data: 附加数据

    Returns:
        边字典
    """
    return {
        'source': source,
        'target': target,
        'relation': relation,
        'weight': weight,
        'data': data or {},
        'timestamp': datetime.now().isoformat()
    }


def build_patient_kg(patient_id: int, patient_data: Dict) -> Dict:
    """
    为单个患者构建知识图谱

    Args:
        patient_id: 患者ID
        patient_data: 患者完整数据(包含病史、检查、用药等)

    Returns:
        知识图谱数据
    """
    nodes = []
    edges = []

    # 1. 创建患者节点
    patient = patient_data.get('patient', {})
    patient_node = build_knowledge_node(
        'patient',
        patient.get('patient_name', f'患者{patient_id}'),
        {
            'patient_id': patient_id,
            'gender': patient.get('gender'),
            'age': calculate_age(patient.get('birth_date'))
        }
    )
    nodes.append(patient_node)

    # 2. 创建疾病节点(基于诊断)
    diagnoses = set()
    for history in patient_data.get('medical_history', []):
        if history.get('diagnosis'):
            diagnoses.add(history['diagnosis'])

    for diagnosis in diagnoses:
        disease_node = build_knowledge_node('disease', diagnosis, {})
        nodes.append(disease_node)
        edges.append(build_knowledge_edge(
            f'patient_{patient_id}', f'disease_{diagnosis}', 'has_disease'
        ))

    # 3. 创建症状节点
    symptoms_count = {}
    for history in patient_data.get('medical_history', []):
        for symptom in history.get('symptoms', []):
            symptoms_count[symptom] = symptoms_count.get(symptom, 0) + 1

    for symptom, count in symptoms_count.items():
        symptom_node = build_knowledge_node('symptom', symptom, {'frequency': count})
        nodes.append(symptom_node)
        edges.append(build_knowledge_edge(
            f'patient_{patient_id}', f'symptom_{symptom}', 'experiences',
            weight=count
        ))

    # 4. 创建检查指标节点
    for report in patient_data.get('lab_reports', []):
        report_date = report.get('report_date', '')
        for indicator in report.get('indicators', []):
            indicator_name = indicator['name']
            indicator_value = indicator['value']

            indicator_node = build_knowledge_node('indicator', indicator_name, {
                'value': indicator_value,
                'unit': indicator.get('unit', ''),
                'is_abnormal': indicator.get('is_abnormal', False),
                'reference_range': indicator.get('reference_range', ''),
                'last_check': report_date
            })
            nodes.append(indicator_node)
            edges.append(build_knowledge_edge(
                f'patient_{patient_id}', f'indicator_{indicator_name}', 'has_result',
                data={'date': report_date}
            ))

            # 如果异常,创建与症状的关联
            if indicator.get('is_abnormal'):
                for symptom in list(symptoms_count.keys())[:3]:  # 关联前3个症状
                    edges.append(build_knowledge_edge(
                        f'indicator_{indicator_name}', f'symptom_{symptom}',
                        'related_to', weight=0.5
                    ))

    # 5. 创建治疗节点(用药)
    for medication in patient_data.get('medications', []):
        med_name = medication['medication_name']
        medication_node = build_knowledge_node('treatment', med_name, {
            'dosage': medication.get('dosage'),
            'frequency': medication.get('frequency'),
            'active': not medication.get('end_date')
        })
        nodes.append(medication_node)
        edges.append(build_knowledge_edge(
            f'patient_{patient_id}', f'treatment_{med_name}', 'takes'
        ))

    # 6. 关联疾病和治疗
    for diagnosis in diagnoses:
        for medication in patient_data.get('medications', [])[:3]:  # 关联前3个用药
            edges.append(build_knowledge_edge(
                f'disease_{diagnosis}', f'treatment_{medication["medication_name"]}',
                'treated_by'
            ))

    return {
        'nodes': nodes,
        'edges': edges,
        'patient_id': patient_id,
        'created_at': datetime.now().isoformat(),
        'statistics': {
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'diseases': len(diagnoses),
            'symptoms': len(symptoms_count),
            'indicators': len([n for n in nodes if n['type'] == 'indicator']),
            'treatments': len([n for n in nodes if n['type'] == 'treatment'])
        }
    }


def calculate_age(birth_date: Optional[str]) -> Optional[int]:
    """
    计算年龄

    Args:
        birth_date: 出生日期字符串

    Returns:
        年龄,无法计算返回None
    """
    if not birth_date:
        return None

    try:
        birth = datetime.strptime(birth_date.split()[0], '%Y-%m-%d')
        today = datetime.now()
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        return age
    except:
        return None


def analyze_disease_progression(kg: Dict) -> Dict:
    """
    分析疾病进展

    Args:
        kg: 知识图谱

    Returns:
        疾病进展分析
    """
    indicators = [n for n in kg['nodes'] if n['type'] == 'indicator']
    abnormal_count = len([i for i in indicators if i['data'].get('is_abnormal')])

    progression = {
        'abnormal_indicators': abnormal_count,
        'total_indicators': len(indicators),
        'severity': 'mild',
        'trend': 'stable'
    }

    if abnormal_count > len(indicators) * 0.5:
        progression['severity'] = 'severe'
    elif abnormal_count > len(indicators) * 0.3:
        progression['severity'] = 'moderate'

    return progression


def export_kg_to_graphviz(kg: Dict, output_path: str):
    """
    将知识图谱导出为Graphviz格式

    Args:
        kg: 知识图谱
        output_path: 输出文件路径
    """
    graphviz = """
digraph SLE_Knowledge_Graph {
    rankdir=LR;
    node [shape=box, style=filled];

"""

    # 添加节点
    node_colors = {
        'patient': 'lightblue',
        'disease': 'lightcoral',
        'symptom': 'lightgreen',
        'indicator': 'lightyellow',
        'treatment': 'lightpink'
    }

    for node in kg['nodes']:
        color = node_colors.get(node['type'], 'white')
        label = node['name']
        graphviz += f'    "{node["type"]}_{node["name"]}" [fillcolor="{color}", label="{label}"];\n'

    # 添加边
    graphviz += "\n"
    for edge in kg['edges']:
        graphviz += f'    "{edge["source"]}" -> "{edge["target"]}" [label="{edge["relation"]}"];\n'

    graphviz += "}\n"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(graphviz)

    print(f"知识图谱已导出到: {output_path}")


def save_kg(kg: Dict, output_path: str):
    """
    保存知识图谱到JSON文件

    Args:
        kg: 知识图谱
        output_path: 输出文件路径
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(kg, f, ensure_ascii=False, indent=2)

    print(f"知识图谱已保存到: {output_path}")


def print_kg_summary(kg: Dict):
    """
    打印知识图谱摘要

    Args:
        kg: 知识图谱
    """
    stats = kg.get('statistics', {})
    print(f"\n知识图谱摘要:")
    print(f"- 患者ID: {kg['patient_id']}")
    print(f"- 节点数: {stats['total_nodes']}")
    print(f"- 边数: {stats['total_edges']}")
    print(f"- 疾病: {stats['diseases']}")
    print(f"- 症状: {stats['symptoms']}")
    print(f"- 指标: {stats['indicators']}")
    print(f"- 治疗方案: {stats['treatments']}")


if __name__ == '__main__':
    # 示例数据
    sample_patient_data = {
        'patient': {
            'patient_id': 1,
            'patient_name': '张三',
            'gender': 'female',
            'birth_date': '1990-01-01'
        },
        'medical_history': [
            {
                'id': 1,
                'patient_id': 1,
                'record_date': '2024-01-15',
                'diagnosis': '系统性红斑狼疮',
                'symptoms': ['关节痛', '皮疹', '疲劳', '发热']
            }
        ],
        'lab_reports': [
            {
                'report_date': '2024-02-01',
                'indicators': [
                    {'name': 'ANA', 'value': '1:320', 'unit': '', 'is_abnormal': True, 'reference_range': '<1:80'},
                    {'name': 'dsDNA', 'value': '阳性', 'unit': '', 'is_abnormal': True, 'reference_range': '阴性'},
                    {'name': 'C3', 'value': '0.5', 'unit': 'g/L', 'is_abnormal': True, 'reference_range': '0.8-1.6'},
                    {'name': 'C4', 'value': '0.08', 'unit': 'g/L', 'is_abnormal': True, 'reference_range': '0.1-0.4'}
                ]
            }
        ],
        'medications': [
            {
                'medication_name': '泼尼松',
                'dosage': '10mg',
                'frequency': '每日1次',
                'active': True
            }
        ]
    }

    # 构建知识图谱
    kg = build_patient_kg(1, sample_patient_data)
    print_kg_summary(kg)

    # 保存
    save_kg(kg, 'sle_knowledge_graph.json')
    export_kg_to_graphviz(kg, 'sle_knowledge_graph.dot')

    # 分析疾病进展
    progression = analyze_disease_progression(kg)
    print(f"\n疾病进展分析:")
    print(f"- 严重程度: {progression['severity']}")
    print(f"- 异常指标: {progression['abnormal_indicators']}/{progression['total_indicators']}")
