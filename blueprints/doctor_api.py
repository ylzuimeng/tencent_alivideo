import logging
import tempfile
import os
from flask import Blueprint, request, jsonify
from utils.time_helpers import serialize_datetime

logger = logging.getLogger(__name__)

doctor_bp = Blueprint('doctor_api', __name__)


@doctor_bp.route('/api/doctors/import', methods=['POST'])
def import_doctors():
    """导入医生信息Excel文件"""
    try:
        from services.doctor_service import doctor_service

        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '没有文件上传'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'}), 400

        if not doctor_service.allowed_file(file.filename):
            return jsonify({'success': False, 'message': '不支持的文件格式，请上传.xlsx或.xls文件'}), 400

        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            file.save(tmp_file.name)
            tmp_file_path = tmp_file.name

        try:
            success, message, doctors = doctor_service.import_from_excel(tmp_file_path)
            if success:
                return jsonify({'success': True, 'message': message, 'count': len(doctors)})
            else:
                return jsonify({'success': False, 'message': message}), 400
        finally:
            try:
                os.unlink(tmp_file_path)
            except Exception:
                pass

    except Exception as e:
        logger.error(f"导入医生信息失败: {str(e)}")
        return jsonify({'success': False, 'message': f'导入失败: {str(e)}'}), 500


@doctor_bp.route('/api/doctors', methods=['GET'])
def get_doctors():
    """获取医生列表"""
    try:
        from services.doctor_service import doctor_service

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search')
        hospital = request.args.get('hospital')
        department = request.args.get('department')
        batch_id = request.args.get('batch_id')

        doctors, total = doctor_service.get_doctors(
            page=page, per_page=per_page, search=search,
            hospital=hospital, department=department, batch_id=batch_id
        )

        return jsonify({
            'success': True,
            'doctors': [
                {
                    'id': d.id, 'name': d.name, 'hospital': d.hospital,
                    'department': d.department, 'title': d.title,
                    'batch_id': d.batch_id, 'is_validated': d.is_validated,
                    'created_at': serialize_datetime(d.created_at, to_beijing=True)
                }
                for d in doctors
            ],
            'total': total, 'per_page': per_page
        })

    except Exception as e:
        logger.error(f"获取医生列表失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取列表失败: {str(e)}'}), 500


@doctor_bp.route('/api/doctors/<int:doctor_id>', methods=['GET'])
def get_doctor(doctor_id):
    try:
        from services.doctor_service import doctor_service
        doctor = doctor_service.get_doctor_by_id(doctor_id)
        if not doctor:
            return jsonify({'success': False, 'message': '医生信息不存在'}), 404

        return jsonify({
            'success': True,
            'doctor': {
                'id': doctor.id, 'name': doctor.name, 'hospital': doctor.hospital,
                'department': doctor.department, 'title': doctor.title,
                'batch_id': doctor.batch_id, 'is_validated': doctor.is_validated,
                'created_at': doctor.created_at.isoformat()
            }
        })

    except Exception as e:
        logger.error(f"获取医生详情失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取详情失败: {str(e)}'}), 500


@doctor_bp.route('/api/doctors/<int:doctor_id>', methods=['PUT'])
def update_doctor(doctor_id):
    try:
        from services.doctor_service import doctor_service
        data = request.get_json()
        success, message = doctor_service.update_doctor(doctor_id, **data)

        if success:
            return jsonify({'success': True, 'message': message})
        return jsonify({'success': False, 'message': message}), 400

    except Exception as e:
        logger.error(f"更新医生信息失败: {str(e)}")
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500


@doctor_bp.route('/api/doctors/<int:doctor_id>', methods=['DELETE'])
def delete_doctor(doctor_id):
    try:
        from services.doctor_service import doctor_service
        success, message = doctor_service.delete_doctor(doctor_id)

        if success:
            return jsonify({'success': True, 'message': message})
        return jsonify({'success': False, 'message': message}), 400

    except Exception as e:
        logger.error(f"删除医生信息失败: {str(e)}")
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500


@doctor_bp.route('/api/doctors/<int:doctor_id>/validate', methods=['POST'])
def validate_doctor(doctor_id):
    try:
        from services.doctor_service import doctor_service
        success, message = doctor_service.validate_doctor(doctor_id)

        if success:
            return jsonify({'success': True, 'message': message})
        return jsonify({'success': False, 'message': message}), 400

    except Exception as e:
        logger.error(f"校验医生信息失败: {str(e)}")
        return jsonify({'success': False, 'message': f'校验失败: {str(e)}'}), 500


@doctor_bp.route('/api/doctors/batches', methods=['GET'])
def get_batches():
    try:
        from services.doctor_service import doctor_service
        batches = doctor_service.get_batch_list()
        return jsonify({'success': True, 'batches': batches})

    except Exception as e:
        logger.error(f"获取批次列表失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取批次列表失败: {str(e)}'}), 500
