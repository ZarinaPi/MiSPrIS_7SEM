"""
API маршруты для работы с перечислениями.
"""

from flask import Blueprint, request, jsonify
from app.models.base import db
from app.models.enumeration import Enumeration, EnumValue, ClassEnum, CarEnumValue
from app.models.car_class import CarClass

enumerations_bp = Blueprint('enumerations', __name__)


@enumerations_bp.route('/enumeration/add', methods=['POST'])
def add_enumeration():
    """Добавление нового справочника-перечисления"""
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'error': 'name обязателен'}), 400
    
    new_enum = Enumeration(
        name=data['name'],
        description=data.get('description'),
        value_type=data.get('value_type', 'string')
    )
    
    try:
        db.session.add(new_enum)
        db.session.commit()
        return jsonify(new_enum.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@enumerations_bp.route('/enumerations', methods=['GET'])
def get_enumerations():
    """Получение списка всех перечислений"""
    enumerations = Enumeration.query.all()
    return jsonify({
        'enumerations': [e.to_dict() for e in enumerations],
        'count': len(enumerations)
    }), 200


@enumerations_bp.route('/enumeration/<int:id_enum>', methods=['GET'])
def get_enumeration(id_enum):
    """Получение перечисления по ID"""
    enumeration = Enumeration.query.get(id_enum)
    if not enumeration:
        return jsonify({'error': 'Перечисление не найдено'}), 404
    
    result = enumeration.to_dict()
    result['values'] = [v.to_dict() for v in enumeration.values]
    result['linked_classes'] = [
        {'id_class': ce.id_class, 'is_required': ce.is_required}
        for ce in enumeration.linked_classes
    ]
    
    return jsonify(result), 200


@enumerations_bp.route('/enumeration/<int:id_enum>', methods=['PUT'])
def update_enumeration(id_enum):
    """Обновление перечисления"""
    data = request.get_json()
    enumeration = Enumeration.query.get(id_enum)
    
    if not enumeration:
        return jsonify({'error': 'Перечисление не найдено'}), 404
    
    if 'name' in data:
        enumeration.name = data['name']
    if 'description' in data:
        enumeration.description = data['description']
    if 'value_type' in data:
        enumeration.value_type = data['value_type']
    
    try:
        db.session.commit()
        return jsonify(enumeration.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@enumerations_bp.route('/enumeration/<int:id_enum>', methods=['DELETE'])
def delete_enumeration(id_enum):
    """Удаление перечисления"""
    enumeration = Enumeration.query.get(id_enum)
    if not enumeration:
        return jsonify({'error': 'Перечисление не найдено'}), 404
    
    # Проверка использования в классах
    if enumeration.linked_classes:
        return jsonify({'error': 'Нельзя удалить перечисление, привязанное к классам'}), 400
    
    try:
        db.session.delete(enumeration)
        db.session.commit()
        return jsonify({'message': 'Перечисление успешно удалено'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@enumerations_bp.route('/enumeration/<int:id_enum>/value/add', methods=['POST'])
def add_enum_value(id_enum):
    """Добавление значения перечисления"""
    data = request.get_json()
    enumeration = Enumeration.query.get(id_enum)
    
    if not enumeration:
        return jsonify({'error': 'Перечисление не найдено'}), 404
    
    if not data or 'value' not in data:
        return jsonify({'error': 'value обязателен'}), 400
    
    new_value = EnumValue(
        id_enum=id_enum,
        value=data['value'],
        sort_order=data.get('sort_order', 0),
        numeric_value=data.get('numeric_value'),
        icon_url=data.get('icon_url'),
        unit_id=data.get('unit_id')
    )
    
    try:
        db.session.add(new_value)
        db.session.commit()
        return jsonify(new_value.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@enumerations_bp.route('/enumeration/<int:id_enum>/values', methods=['GET'])
def get_enum_values(id_enum):
    """Получение значений перечисления"""
    enumeration = Enumeration.query.get(id_enum)
    if not enumeration:
        return jsonify({'error': 'Перечисление не найдено'}), 404
    
    values = EnumValue.query.filter_by(id_enum=id_enum).order_by(EnumValue.sort_order).all()
    return jsonify({
        'values': [v.to_dict() for v in values],
        'count': len(values)
    }), 200


@enumerations_bp.route('/enum-value/<int:id_value>', methods=['PUT'])
def update_enum_value(id_value):
    """Обновление значения перечисления"""
    data = request.get_json()
    enum_value = EnumValue.query.get(id_value)
    
    if not enum_value:
        return jsonify({'error': 'Значение не найдено'}), 404
    
    if 'value' in data:
        enum_value.value = data['value']
    if 'sort_order' in data:
        enum_value.sort_order = data['sort_order']
    if 'numeric_value' in data:
        enum_value.numeric_value = data['numeric_value']
    if 'icon_url' in data:
        enum_value.icon_url = data['icon_url']
    if 'unit_id' in data:
        enum_value.unit_id = data['unit_id']
    
    try:
        db.session.commit()
        return jsonify(enum_value.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@enumerations_bp.route('/enum-value/<int:id_value>', methods=['DELETE'])
def delete_enum_value(id_value):
    """Удаление значения перечисления"""
    enum_value = EnumValue.query.get(id_value)
    if not enum_value:
        return jsonify({'error': 'Значение не найдено'}), 404
    
    # Проверка использования
    if CarEnumValue.query.filter_by(id_value=id_value).first():
        return jsonify({'error': 'Нельзя удалить значение, используемое в автомобилях'}), 400
    
    try:
        db.session.delete(enum_value)
        db.session.commit()
        return jsonify({'message': 'Значение успешно удалено'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@enumerations_bp.route('/class/<int:id_class>/enum/link', methods=['POST'])
def link_enum_to_class(id_class):
    """Привязка перечисления к классу автомобилей"""
    data = request.get_json()
    car_class = CarClass.query.get(id_class)
    
    if not car_class:
        return jsonify({'error': 'Класс не найден'}), 404
    
    id_enum = data.get('id_enum')
    is_required = data.get('is_required', False)
    
    if not id_enum:
        return jsonify({'error': 'id_enum обязателен'}), 400
    
    enumeration = Enumeration.query.get(id_enum)
    if not enumeration:
        return jsonify({'error': 'Перечисление не найдено'}), 404
    
    # Проверяем существование связи
    existing = ClassEnum.query.filter_by(id_class=id_class, id_enum=id_enum).first()
    if existing:
        return jsonify({'error': 'Перечисление уже привязано к классу'}), 400
    
    new_link = ClassEnum(
        id_class=id_class,
        id_enum=id_enum,
        is_required=is_required
    )
    
    try:
        db.session.add(new_link)
        db.session.commit()
        return jsonify({
            'id_class': id_class,
            'id_enum': id_enum,
            'is_required': is_required
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@enumerations_bp.route('/class/<int:id_class>/enums', methods=['GET'])
def get_class_enums(id_class):
    """Получение перечислений, привязанных к классу"""
    car_class = CarClass.query.get(id_class)
    if not car_class:
        return jsonify({'error': 'Класс не найден'}), 404
    
    class_enums = ClassEnum.query.filter_by(id_class=id_class).all()
    
    result = []
    for ce in class_enums:
        enum_data = ce.enumeration.to_dict()
        enum_data['is_required'] = ce.is_required
        enum_data['values'] = [v.to_dict() for v in ce.enumeration.values]
        result.append(enum_data)
    
    return jsonify({
        'enumerations': result,
        'count': len(result)
    }), 200
