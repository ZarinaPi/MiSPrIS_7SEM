"""
API маршруты для работы с автомобилями.
"""

from flask import Blueprint, request, jsonify
from app.models.base import db
from app.models.car import Car
from app.models.car_class import CarClass
from app.models.enumeration import CarEnumValue, Enumeration, EnumValue
from app.models.parameter import CarParameter, Parameter, ClassParameter
from sqlalchemy.orm import joinedload, selectinload

cars_bp = Blueprint('cars', __name__)


@cars_bp.route('/car/add', methods=['POST'])
def add_car():
    """Добавление нового автомобиля"""
    data = request.get_json()
    
    if not data or 'short_name' not in data or 'id_class' not in data:
        return jsonify({'error': 'short_name и id_class обязательны'}), 400
    
    # Проверка существования класса
    car_class = CarClass.query.get(data['id_class'])
    if not car_class:
        return jsonify({'error': 'Класс не найден'}), 404
    
    new_car = Car(
        short_name=data['short_name'],
        id_class=data['id_class']
    )
    
    try:
        db.session.add(new_car)
        db.session.commit()
        return jsonify(new_car.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@cars_bp.route('/car/<int:id_car>', methods=['DELETE'])
def delete_car(id_car):
    """Удаление автомобиля"""
    car = Car.query.get(id_car)
    if not car:
        return jsonify({'error': 'Автомобиль не найден'}), 404
    
    try:
        db.session.delete(car)
        db.session.commit()
        return jsonify({'message': 'Автомобиль успешно удален'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@cars_bp.route('/car/<int:id_car>', methods=['PUT'])
def update_car(id_car):
    """Обновление автомобиля"""
    data = request.get_json()
    car = Car.query.get(id_car)
    
    if not car:
        return jsonify({'error': 'Автомобиль не найден'}), 404
    
    if 'short_name' in data:
        car.short_name = data['short_name']
    if 'id_class' in data:
        car_class = CarClass.query.get(data['id_class'])
        if not car_class:
            return jsonify({'error': 'Класс не найден'}), 404
        car.id_class = data['id_class']
    
    try:
        db.session.commit()
        return jsonify(car.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@cars_bp.route('/cars', methods=['GET'])
def get_cars():
    """Получение списка всех автомобилей"""
    cars = Car.query.options(selectinload(Car.car_class)).all()
    return jsonify({
        'cars': [c.to_dict() for c in cars],
        'count': len(cars)
    }), 200


@cars_bp.route('/cars/<int:id_class>', methods=['GET'])
def get_cars_by_class(id_class):
    """Получение автомобилей по классу"""
    car_class = CarClass.query.get(id_class)
    if not car_class:
        return jsonify({'error': 'Класс не найден'}), 404
    
    # Получаем все дочерние классы
    all_children = car_class.get_all_children()
    child_ids = [c.id_class for c in all_children] + [id_class]
    
    cars = Car.query.filter(Car.id_class.in_(child_ids)).all()
    return jsonify({
        'cars': [c.to_dict() for c in cars],
        'count': len(cars)
    }), 200


@cars_bp.route('/car/<int:id_car>/attributes', methods=['GET'])
def get_car_attributes(id_car):
    """Получение атрибутов (перечислений) автомобиля"""
    car = Car.query.get(id_car)
    if not car:
        return jsonify({'error': 'Автомобиль не найден'}), 404
    
    attributes = CarEnumValue.query.filter_by(id_car=id_car).all()
    return jsonify({
        'attributes': [a.to_dict() for a in attributes],
        'count': len(attributes)
    }), 200


@cars_bp.route('/car/<int:id_car>/attribute', methods=['PUT'])
def set_car_attribute(id_car):
    """Установка атрибута (перечисления) автомобиля"""
    data = request.get_json()
    car = Car.query.get(id_car)
    
    if not car:
        return jsonify({'error': 'Автомобиль не найден'}), 404
    
    id_enum = data.get('id_enum')
    id_value = data.get('id_value')
    
    if not id_enum or not id_value:
        return jsonify({'error': 'id_enum и id_value обязательны'}), 400
    
    # Проверка существования
    enumeration = Enumeration.query.get(id_enum)
    enum_value = EnumValue.query.get(id_value)
    
    if not enumeration or not enum_value:
        return jsonify({'error': 'Перечисление или значение не найдено'}), 404
    
    # Проверяем привязку перечисления к классу автомобиля
    class_enum = ClassEnum.query.filter_by(
        id_class=car.id_class,
        id_enum=id_enum
    ).first()
    
    if not class_enum:
        return jsonify({'error': 'Перечисление не привязано к классу автомобиля'}), 400
    
    # Обновляем или создаем запись
    car_attr = CarEnumValue.query.filter_by(id_car=id_car, id_enum=id_enum).first()
    
    if car_attr:
        car_attr.id_value = id_value
    else:
        car_attr = CarEnumValue(
            id_car=id_car,
            id_enum=id_enum,
            id_value=id_value
        )
        db.session.add(car_attr)
    
    try:
        db.session.commit()
        return jsonify(car_attr.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@cars_bp.route('/car/<int:id_car>/parameters/batch', methods=['PUT'])
def batch_update_parameters(id_car):
    """Массовое обновление параметров автомобиля"""
    data = request.get_json()
    car = Car.query.get(id_car)
    
    if not car:
        return jsonify({'error': 'Автомобиль не найден'}), 404
    
    parameters_data = data.get('parameters', [])
    
    try:
        for param_data in parameters_data:
            id_param = param_data.get('id_param')
            value = param_data.get('value')
            enum_value_id = param_data.get('enum_value_id')
            
            parameter = Parameter.query.get(id_param)
            if not parameter:
                continue
            
            # Проверка привязки параметра к классу
            class_param = ClassParameter.query.filter_by(
                id_class=car.id_class,
                id_param=id_param
            ).first()
            
            if not class_param:
                continue
            
            # Находим или создаем запись
            car_param = CarParameter.query.filter_by(
                id_car=id_car,
                id_param=id_param
            ).first()
            
            if not car_param:
                car_param = CarParameter(
                    id_car=id_car,
                    id_param=id_param
                )
                db.session.add(car_param)
            
            # Установка значения в зависимости от типа
            vt = parameter.value_type
            if vt == 'numeric':
                car_param.val_r = float(value) if value else None
            elif vt == 'integer':
                car_param.val_int = int(value) if value else None
            elif vt == 'string':
                car_param.val_str = str(value) if value else None
            elif vt == 'datetime':
                from datetime import datetime
                car_param.val_datetime = datetime.fromisoformat(value) if value else None
            elif vt == 'enum':
                car_param.enum_val = enum_value_id
        
        db.session.commit()
        return jsonify({'message': 'Параметры успешно обновлены'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@cars_bp.route('/car/<int:id_car>/details', methods=['GET'])
def get_car_details(id_car):
    """Получение полной информации об автомобиле"""
    car = Car.query.options(
        selectinload(Car.car_class),
        selectinload(Car.attributes),
        selectinload(Car.parameters)
    ).get(id_car)
    
    if not car:
        return jsonify({'error': 'Автомобиль не найден'}), 404
    
    result = car.to_dict()
    result['parameters'] = [p.to_dict() for p in car.parameters]
    
    return jsonify(result), 200


@cars_bp.route('/cars/filter', methods=['POST'])
def filter_cars():
    """Фильтрация автомобилей по параметрам"""
    data = request.get_json()
    filters = data.get('filters', {})
    
    query = Car.query
    
    # Фильтр по классу
    if 'id_class' in filters:
        car_class = CarClass.query.get(filters['id_class'])
        if car_class:
            children = car_class.get_all_children()
            child_ids = [c.id_class for c in children] + [filters['id_class']]
            query = query.filter(Car.id_class.in_(child_ids))
    
    # Фильтр по параметрам
    if 'parameters' in filters:
        for param_filter in filters['parameters']:
            id_param = param_filter.get('id_param')
            min_val = param_filter.get('min')
            max_val = param_filter.get('max')
            exact_val = param_filter.get('value')
            
            if id_param:
                query = query.join(CarParameter).filter(
                    CarParameter.id_param == id_param
                )
                
                if min_val is not None:
                    query = query.filter(CarParameter.val_r >= min_val)
                if max_val is not None:
                    query = query.filter(CarParameter.val_r <= max_val)
                if exact_val is not None:
                    query = query.filter(CarParameter.val_str == str(exact_val))
    
    cars = query.all()
    return jsonify({
        'cars': [c.to_dict() for c in cars],
        'count': len(cars)
    }), 200
