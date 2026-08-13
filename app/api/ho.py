"""
API маршруты для работы с хозяйственными операциями.
"""

from flask import Blueprint, request, jsonify
from app.models.base import db
from app.models.ho import (
    HOClass, HOInstance, HOActor, HOParameterValue, HOPosition,
    EconomicEntity, Role, HOClassRole, HOParameter, HOClassParameter
)
from app.models.car import Car
from datetime import datetime

ho_bp = Blueprint('ho', __name__)


@ho_bp.route('/ho/class/add', methods=['POST'])
def ins_ho_class():
    """Добавление класса хозяйственной операции"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'code' not in data:
        return jsonify({'error': 'name и code обязательны'}), 400
    
    new_class = HOClass(
        name=data['name'],
        code=data['code'],
        parent_id=data.get('parent_id')
    )
    
    try:
        db.session.add(new_class)
        db.session.commit()
        return jsonify(new_class.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ho_bp.route('/ho/class/<int:id_ho_class>/parameter/link', methods=['POST'])
def add_param_to_ho_class(id_ho_class):
    """Привязка параметра к классу хозяйственной операции"""
    data = request.get_json()
    ho_class = HOClass.query.get(id_ho_class)
    
    if not ho_class:
        return jsonify({'error': 'Класс не найден'}), 404
    
    id_param = data.get('id_param')
    if not id_param:
        return jsonify({'error': 'id_param обязателен'}), 400
    
    parameter = HOParameter.query.get(id_param)
    if not parameter:
        return jsonify({'error': 'Параметр не найден'}), 404
    
    existing = HOClassParameter.query.filter_by(
        id_ho_class=id_ho_class,
        id_param=id_param
    ).first()
    
    if existing:
        return jsonify({'error': 'Параметр уже привязан'}), 400
    
    new_link = HOClassParameter(
        id_ho_class=id_ho_class,
        id_param=id_param,
        sort_order=data.get('sort_order', 0),
        min_value=data.get('min_value'),
        max_value=data.get('max_value'),
        is_required=data.get('is_required', False)
    )
    
    try:
        db.session.add(new_link)
        db.session.commit()
        return jsonify({
            'id_ho_class': id_ho_class,
            'id_param': id_param,
            'is_required': new_link.is_required
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ho_bp.route('/ho/class/<int:id_ho_class>/role/link', methods=['POST'])
def add_role_to_ho_class(id_ho_class):
    """Привязка роли к классу хозяйственной операции"""
    data = request.get_json()
    ho_class = HOClass.query.get(id_ho_class)
    
    if not ho_class:
        return jsonify({'error': 'Класс не найден'}), 404
    
    id_role = data.get('id_role')
    if not id_role:
        return jsonify({'error': 'id_role обязателен'}), 400
    
    role = Role.query.get(id_role)
    if not role:
        return jsonify({'error': 'Роль не найдена'}), 404
    
    new_link = HOClassRole(
        id_ho_class=id_ho_class,
        id_role=id_role,
        is_required=data.get('is_required', True)
    )
    
    try:
        db.session.add(new_link)
        db.session.commit()
        return jsonify({
            'id_ho_class': id_ho_class,
            'id_role': id_role,
            'is_required': new_link.is_required
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ho_bp.route('/ho/instance/add', methods=['POST'])
def ins_ho():
    """Создание экземпляра хозяйственной операции"""
    data = request.get_json()
    
    if not data or 'id_ho_class' not in data:
        return jsonify({'error': 'id_ho_class обязателен'}), 400
    
    ho_class = HOClass.query.get(data['id_ho_class'])
    if not ho_class:
        return jsonify({'error': 'Класс не найден'}), 404
    
    new_ho = HOInstance(
        id_ho_class=data['id_ho_class'],
        doc_number=data.get('doc_number'),
        doc_date=datetime.strptime(data['doc_date'], '%Y-%m-%d').date() if data.get('doc_date') else None,
        total_amount=data.get('total_amount')
    )
    
    try:
        db.session.add(new_ho)
        db.session.commit()
        return jsonify(new_ho.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ho_bp.route('/ho/<int:id_ho>/actor', methods=['PUT'])
def set_ho_actor(id_ho):
    """Назначение участника хозяйственной операции"""
    data = request.get_json()
    ho = HOInstance.query.get(id_ho)
    
    if not ho:
        return jsonify({'error': 'Хозяйственная операция не найдена'}), 404
    
    id_role = data.get('id_role')
    id_sxd = data.get('id_sxd')
    
    if not id_role or not id_sxd:
        return jsonify({'error': 'id_role и id_sxd обязательны'}), 400
    
    actor = HOActor.query.filter_by(id_ho=id_ho, id_role=id_role).first()
    
    if actor:
        actor.id_sxd = id_sxd
    else:
        actor = HOActor(
            id_ho=id_ho,
            id_role=id_role,
            id_sxd=id_sxd
        )
        db.session.add(actor)
    
    try:
        db.session.commit()
        return jsonify({
            'id_ho': id_ho,
            'id_role': id_role,
            'id_sxd': id_sxd
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ho_bp.route('/ho/<int:id_ho>/parameter', methods=['PUT'])
def write_ho_par(id_ho):
    """Установка значения параметра хозяйственной операции"""
    data = request.get_json()
    ho = HOInstance.query.get(id_ho)
    
    if not ho:
        return jsonify({'error': 'Хозяйственная операция не найдена'}), 404
    
    id_param = data.get('id_param')
    value = data.get('value')
    enum_value_id = data.get('enum_value_id')
    
    if not id_param:
        return jsonify({'error': 'id_param обязателен'}), 400
    
    parameter = HOParameter.query.get(id_param)
    if not parameter:
        return jsonify({'error': 'Параметр не найден'}), 404
    
    ho_par = HOParameterValue.query.filter_by(id_ho=id_ho, id_param=id_param).first()
    
    if not ho_par:
        ho_par = HOParameterValue(id_ho=id_ho, id_param=id_param)
        db.session.add(ho_par)
    
    vt = parameter.value_type
    if vt == 'numeric':
        ho_par.val_r = float(value) if value is not None else None
    elif vt == 'integer':
        ho_par.val_int = int(value) if value is not None else None
    elif vt == 'string':
        ho_par.val_str = str(value) if value is not None else None
    elif vt == 'datetime':
        ho_par.val_datetime = datetime.fromisoformat(value) if value else None
    elif vt == 'enum':
        ho_par.enum_val = enum_value_id
    
    try:
        db.session.commit()
        return jsonify({'message': 'Параметр успешно установлен'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ho_bp.route('/ho/<int:id_ho>/position/add', methods=['POST'])
def add_ho_position(id_ho):
    """Добавление позиции в хозяйственную операцию"""
    data = request.get_json()
    ho = HOInstance.query.get(id_ho)
    
    if not ho:
        return jsonify({'error': 'Хозяйственная операция не найдена'}), 404
    
    id_car = data.get('id_car')
    quantity = data.get('quantity', 1.0)
    price = data.get('price')
    
    if not id_car:
        return jsonify({'error': 'id_car обязателен'}), 400
    
    car = Car.query.get(id_car)
    if not car:
        return jsonify({'error': 'Автомобиль не найден'}), 404
    
    amount = quantity * price if price else 0
    
    new_position = HOPosition(
        id_ho=id_ho,
        id_car=id_car,
        quantity=quantity,
        price=price,
        amount=amount
    )
    
    try:
        db.session.add(new_position)
        
        # Обновляем общую сумму
        total = db.session.query(db.func.sum(HOPosition.amount)).filter_by(id_ho=id_ho).scalar()
        ho.total_amount = total
        
        db.session.commit()
        return jsonify({
            'id_position': new_position.id_position,
            'quantity': new_position.quantity,
            'price': new_position.price,
            'amount': new_position.amount
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ho_bp.route('/ho/class/<int:id_ho_class>/find', methods=['GET'])
def find_ho_by_class(id_ho_class):
    """Поиск хозяйственных операций по классу"""
    ho_class = HOClass.query.get(id_ho_class)
    if not ho_class:
        return jsonify({'error': 'Класс не найден'}), 404
    
    ho_instances = HOInstance.query.filter_by(id_ho_class=id_ho_class).all()
    
    result = []
    for ho in ho_instances:
        actors = HOActor.query.filter_by(id_ho=ho.id_ho).all()
        params = HOParameterValue.query.filter_by(id_ho=ho.id_ho).all()
        positions = HOPosition.query.filter_by(id_ho=ho.id_ho).all()
        
        result.append({
            'ho': ho.to_dict(),
            'actors': [
                {'id_role': a.id_role, 'role_name': a.role.name, 'sxd': a.sxd.to_dict()}
                for a in actors
            ],
            'parameters': [p.to_dict() for p in params],
            'positions': [
                {
                    'id_car': pos.id_car,
                    'car_name': pos.car.short_name if pos.car else None,
                    'quantity': pos.quantity,
                    'price': pos.price,
                    'amount': pos.amount
                }
                for pos in positions
            ]
        })
    
    return jsonify({
        'ho_instances': result,
        'count': len(result)
    }), 200
