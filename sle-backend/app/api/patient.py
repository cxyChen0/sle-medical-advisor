from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

# 模拟患者数据
dummy_patient_data = {
    '1': {
        'name': '患者1',
        'age': 35,
        'gender': '女',
        'history': [
            {
                'test_id': 1,
                'date': '2026-01-01',
                'type': 'blood',
                'data': {
                    '白细胞计数': 4.5,
                    '红细胞计数': 4.8,
                    '血小板计数': 220
                }
            },
            {
                'test_id': 2,
                'date': '2026-01-08',
                'type': 'blood',
                'data': {
                    '白细胞计数': 4.2,
                    '红细胞计数': 4.7,
                    '血小板计数': 210
                }
            },
            {
                'test_id': 3,
                'date': '2026-01-15',
                'type': 'blood',
                'data': {
                    '白细胞计数': 3.8,
                    '红细胞计数': 4.6,
                    '血小板计数': 200
                }
            },
            {
                'test_id': 4,
                'date': '2026-01-22',
                'type': 'blood',
                'data': {
                    '白细胞计数': 4.0,
                    '红细胞计数': 4.5,
                    '血小板计数': 215
                }
            },
            {
                'test_id': 5,
                'date': '2026-01-29',
                'type': 'blood',
                'data': {
                    '白细胞计数': 4.3,
                    '红细胞计数': 4.7,
                    '血小板计数': 225
                }
            },
            {
                'test_id': 6,
                'date': '2026-02-05',
                'type': 'blood',
                'data': {
                    '白细胞计数': 4.6,
                    '红细胞计数': 4.8,
                    '血小板计数': 230
                }
            }
        ]
    }
}

bp = Blueprint('patient', __name__, url_prefix='/api/patient')

@bp.route('/<patient_id>', methods=['GET'])
def get_patient_data(patient_id):
    if patient_id not in dummy_patient_data:
        return jsonify({'error': '患者不存在'}), 404

    return jsonify(dummy_patient_data[patient_id]), 200

@bp.route('/<patient_id>/history', methods=['GET'])
def get_patient_history(patient_id):
    if patient_id not in dummy_patient_data:
        return jsonify({'error': '患者不存在'}), 404

    test_type = request.args.get('type', 'blood')
    history = dummy_patient_data[patient_id]['history']
    filtered_history = [h for h in history if h['type'] == test_type]

    return jsonify(filtered_history), 200

@bp.route('/<patient_id>/upload', methods=['POST'])
def upload_patient_data(patient_id):
    # 模拟上传功能
    data = request.get_json()
    print('上传数据:', data)

    return jsonify({'message': '上传成功'}), 201

@bp.route('/<patient_id>/abnormal', methods=['GET'])
def get_abnormal_indices(patient_id):
    # 模拟异常指标检测
    abnormal_indices = [
        {
            'test_id': 3,
            'date': '2026-01-15',
            'index': '白细胞计数',
            'value': 3.8,
            'reference_range': '4.0-10.0',
            'status': '异常'
        },
        {
            'test_id': 3,
            'date': '2026-01-15',
            'index': '尿蛋白',
            'value': '1+',
            'reference_range': '阴性',
            'status': '异常'
        },
        {
            'test_id': 3,
            'date': '2026-01-15',
            'index': 'ANA',
            'value': '1:320',
            'reference_range': '<1:80',
            'status': '异常'
        }
    ]

    return jsonify(abnormal_indices), 200
