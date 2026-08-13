"""
API маршруты для работы с параметрами.
"""

from flask import Blueprint, request, jsonify
from app.models.base import db
from app.models.parameter import Parameter, ClassParameter, CarParameter, ParameterGroup
from app.models.car_class import CarClass
from app.models.car import Car
from sqlalchemy.orm import selectinload

parameters_bp = Blueprint('parameters', __name__)


@parameters_bp.route('/parameter/add', methods=['POST'])
def add_parameter():
    """Добавление нового параметра"""
    data = request.get_json()
    
    if not data or 'code' not in data or 'name' not in data or 'value_type' not in data:
        return jsonify({'error': 'code, name и value_type обязательны'}), 400
    
    new_param = Parameter(
        code=data['code'],
        name=data['name'],
        description=data.get('description'),
        value_type=data['value_type'],
        unit_id=data.get('unit_id'),
        enum_id=data.get('enum_id')
    )
    
    try:
        db.session.add(new_param)
        db.session.commit()
        return jsonify(new_param.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@parameters_bp.route('/parameters', methods=['GET'])
def get_parameters():
    """Получение списка всех параметров"""
    parameters = Parameter.query.all()
    return jsonify({
        'parameters': [p.to_dict() for p in parameters],
        'count': len(parameters)
    }), 200


@parameters_bp.route('/parameter/<int:id_param>', methods=['GET'])
def get_parameter(id_param):
    """Получение параметра по ID"""
    parameter = Parameter.query.get(id_param)
    if not parameter:
        return jsonify({'error': 'Параметр не найден'}), 404
    
    return jsonify(parameter.to_dict()), 200


@parameters_bp.route('/parameter/<int:id_param>', methods=['PUT'])
def update_parameter(id_param):
    """Обновление параметра"""
    data = request.get_json()
    parameter = Parameter.query.get(id_param)
    
    if not parameter:
        return jsonify({'error': 'Параметр не найден'}), 404
    
    if 'code' in data:
        parameter.code = data['code']
    if 'name' in data:
        parameter.name = data['name']
    if 'description' in data:
        parameter.description = data['description']
    if 'value_type' in data:
        parameter.value_type = data['value_type']
    if 'unit_id' in data:
        parameter.unit_id = data['unit_id']
    if 'enum_id' in data:
        parameter.enum_id = data['enum_id']
    
    try:
        db.session.commit()
        return jsonify(parameter.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@parameters_bp.route('/parameter/<int:id_param>', methods=['DELETE'])
def delete_parameter(id_param):
    """Удаление параметра"""
    parameter = Parameter.query.get(id_param)
    if not parameter:
        return jsonify({'error': 'Параметр не найден'}), 404
    
    # Проверка использования
    if ClassParameter.query.filter_by(id_param=id_param).first():
        return jsonify({'error': 'Нельзя удалить параметр, привязанный к классам'}), 400
    
    try:
        db.session.delete(parameter)
        db.session.commit()
        return jsonify({'message': 'Параметр успешно удален'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@parameters_bp.route('/class/<int:id_class>/parameter/link', methods=['POST'])
def link_parameter_to_class(id_class):
    """Привязка параметра к классу автомобилей"""
    data = request.get_json()
    car_class = CarClass.query.get(id_class)
    
    if not car_class:
        return jsonify({'error': 'Класс не найден'}), 404
    
    id_param = data.get('id_param')
    if not id_param:
        return jsonify({'error': 'id_param обязателен'}), 400
    
    parameter = Parameter.query.get(id_param)
    if not parameter:
        return jsonify({'error': 'Параметр не найден'}), 404
    
    # Проверка существующей привязки
    existing = ClassParameter.query.filter_by(id_class=id_class, id_param=id_param).first()
    if existing:
        return jsonify({'error': 'Параметр уже привязан к классу'}), 400
    
    new_link = ClassParameter(
        id_class=id_class,
        id_param=id_param,
        is_required=data.get('is_required', False),
        sort_order=data.get('sort_order', 0),
        min_value=data.get('min_value'),
        max_value=data.get('max_value'),
        id_group=data.get('id_group')
    )
    
    try:
        db.session.add(new_link)
        db.session.commit()
        return jsonify(new_link.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@parameters_bp.route('/class/<int:id_class>/parameters', methods=['GET'])
def get_class_parameters(id_class):
    """Получение параметров, привязанных к классу"""
    car_class = CarClass.query.get(id_class)
    if not car_class:
        return jsonify({'error': 'Класс не найден'}), 404
    
    class_params = ClassParameter.query.filter_by(id_class=id_class).all()
    
    return jsonify({
        'parameters': [cp.to_dict() for cp in class_params],
        'count': len(class_params)
    }), 200


@parameters_bp.route('/class/<int:id_class>/group', methods=['POST'])
def create_parameter_group(id_class):
    """Создание группы параметров"""
    data = request.get_json()
    car_class = CarClass.query.get(id_class)
    
    if not car_class:
        return jsonify({'error': 'Класс не найден'}), 404
    
    if not data or 'name' not in data:
        return jsonify({'error': 'name обязателен'}), 400
    
    new_group = ParameterGroup(
        id_class=id_class,
        name=data['name'],
        sort_order=data.get('sort_order', 0)
    )
    
    try:
        db.session.add(new_group)
        db.session.commit()
        return jsonify({
            'id_group': new_group.id_group,
            'name': new_group.name,
            'sort_order': new_group.sort_order
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@parameters_bp.route('/class/<int:id_class>/parameter/<int:id_param>/group', methods=['PUT'])
def assign_param_to_group(id_class, id_param):
    """Назначение параметра группе"""
    data = request.get_json()
    id_group = data.get('id_group')
    
    class_param = ClassParameter.query.filter_by(
        id_class=id_class,
        id_param=id_param
    ).first()
    
    if not class_param:
        return jsonify({'error': 'Параметр не привязан к классу'}), 404
    
    class_param.id_group = id_group
    
    try:
        db.session.commit()
        return jsonify(class_param.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@parameters_bp.route('/class/<int:id_class>/parameters/grouped', methods=['GET'])
def get_class_parameters_grouped(id_class):
    """Получение параметров класса, сгруппированных по группам"""
    car_class = CarClass.query.get(id_class)
    if not car_class:
        return jsonify({'error': 'Класс не найден'}), 404
    
    # Получаем все параметры класса
    class_params = ClassParameter.query.filter_by(id_class=id_class).all()
    
    # Группируем
    groups = {}
    ungrouped = []
    
    for cp in class_params:
        if cp.id_group:
            group_key = cp.group.name if cp.group else f'Группа {cp.id_group}'
            if group_key not in groups:
                groups[group_key] = {
                    'id_group': cp.id_group,
                    'name': group_key,
                    'sort_order': cp.group.sort_order if cp.group else 0,
                    'parameters': []
                }
            groups[group_key]['parameters'].append(cp.to_dict())
        else:
            ungrouped.append(cp.to_dict())
    
    result = {
        'groups': list(groups.values()),
        'ungrouped': ungrouped
    }
    
    return jsonify(result), 200


@parameters_bp.route('/car/<int:id_car>/parameter', methods=['PUT'])
def set_car_parameter(id_car):
    """Установка значения параметра автомобиля"""
    data = request.get_json()
    car = Car.query.get(id_car)
    
    if not car:
        return jsonify({'error': 'Автомобиль не найден'}), 404
    
    id_param = data.get('id_param')
    value = data.get('value')
    enum_value_id = data.get('enum_value_id')
    
    if not id_param:
        return jsonify({'error': 'id_param обязателен'}), 400
    
    parameter = Parameter.query.get(id_param)
    if not parameter:
        return jsonify({'error': 'Параметр не найден'}), 404
    
    # Проверка привязки параметра к классу
    class_param = ClassParameter.query.filter_by(
        id_class=car.id_class,
        id_param=id_param
    ).first()
    
    if not class_param:
        return jsonify({'error': 'Параметр не привязан к классу автомобиля'}), 400
    
    # Валидация значения
    if class_param.min_value is not None and value is not None and value < class_param.min_value:
        return jsonify({'error': f'Значение меньше минимального ({class_param.min_value})'}), 400
    
    if class_param.max_value is not None and value is not None and value > class_param.max_value:
        return jsonify({'error': f'Значение больше максимального ({class_param.max_value})'}), 400
    
    # Находим или создаем запись
    car_param = CarParameter.query.filter_by(id_car=id_car, id_param=id_param).first()
    
    if not car_param:
        car_param = CarParameter(id_car=id_car, id_param=id_param)
        db.session.add(car_param)
    
    # Установка значения в зависимости от типа
    vt = parameter.value_type
    if vt == 'numeric':
        car_param.val_r = float(value) if value is not None else None
    elif vt == 'integer':
        car_param.val_int = int(value) if value is not None else None
    elif vt == 'string':
        car_param.val_str = str(value) if value is not None else None
    elif vt == 'datetime':
        from datetime import datetime
        car_param.val_datetime = datetime.fromisoformat(value) if value else None
    elif vt == 'enum':
        car_param.enum_val = enum_value_id
    
    try:
        db.session.commit()
        return jsonify(car_param.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
