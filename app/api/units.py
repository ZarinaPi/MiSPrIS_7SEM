"""
API маршруты для работы с единицами измерения.
"""

from flask import Blueprint, request, jsonify
from app.models.base import db
from app.models.unit import Unit

units_bp = Blueprint('units', __name__)


@units_bp.route('/units', methods=['GET'])
def get_units():
    """Получение списка всех единиц измерения"""
    units = Unit.query.all()
    return jsonify({
        'units': [u.to_dict() for u in units],
        'count': len(units)
    }), 200


@units_bp.route('/unit/<int:id_ei>', methods=['GET'])
def get_unit(id_ei):
    """Получение единицы измерения по ID"""
    unit = Unit.query.get(id_ei)
    if not unit:
        return jsonify({'error': 'Единица измерения не найдена'}), 404
    
    return jsonify(unit.to_dict()), 200


@units_bp.route('/unit/add', methods=['POST'])
def add_unit():
    """Добавление новой единицы измерения"""
    data = request.get_json()
    
    if not data or 'short_name' not in data or 'name' not in data:
        return jsonify({'error': 'short_name и name обязательны'}), 400
    
    new_unit = Unit(
        short_name=data['short_name'],
        name=data['name']
    )
    
    try:
        db.session.add(new_unit)
        db.session.commit()
        return jsonify(new_unit.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@units_bp.route('/unit/<int:id_ei>', methods=['PUT'])
def update_unit(id_ei):
    """Обновление единицы измерения"""
    data = request.get_json()
    unit = Unit.query.get(id_ei)
    
    if not unit:
        return jsonify({'error': 'Единица измерения не найдена'}), 404
    
    if 'short_name' in data:
        unit.short_name = data['short_name']
    if 'name' in data:
        unit.name = data['name']
    
    try:
        db.session.commit()
        return jsonify(unit.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@units_bp.route('/unit/<int:id_ei>', methods=['DELETE'])
def delete_unit(id_ei):
    """Удаление единицы измерения"""
    unit = Unit.query.get(id_ei)
    if not unit:
        return jsonify({'error': 'Единица измерения не найдена'}), 404
    
    # Проверка использования
    from app.models.parameter import Parameter
    from app.models.enumeration import EnumValue
    
    if Parameter.query.filter_by(unit_id=id_ei).first():
        return jsonify({'error': 'Нельзя удалить единицу, используемую в параметрах'}), 400
    
    if EnumValue.query.filter_by(unit_id=id_ei).first():
        return jsonify({'error': 'Нельзя удалить единицу, используемую в перечислениях'}), 400
    
    try:
        db.session.delete(unit)
        db.session.commit()
        return jsonify({'message': 'Единица измерения успешно удалена'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
