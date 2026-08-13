"""
API маршруты для работы с классами автомобилей.
"""

from flask import Blueprint, request, jsonify
from app.models.base import db
from app.models.car_class import CarClass
from app.models.unit import Unit
from sqlalchemy.orm import joinedload

car_classes_bp = Blueprint('car_classes', __name__)


@car_classes_bp.route('/class/add', methods=['POST'])
def add_class():
    """Добавление нового класса автомобилей"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'short_name' not in data:
        return jsonify({'error': 'name и short_name обязательны'}), 400
    
    # Проверка на цикл
    main_class_id = data.get('main_class')
    if main_class_id:
        temp = CarClass.query.get(main_class_id)
        while temp:
            if temp.id_class == main_class_id:
                return jsonify({'error': 'Обнаружен цикл в иерархии'}), 400
            temp = temp.parent
    
    new_class = CarClass(
        name=data['name'],
        short_name=data['short_name'],
        base_ei=data.get('base_ei'),
        main_class=main_class_id
    )
    
    try:
        db.session.add(new_class)
        db.session.commit()
        return jsonify(new_class.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@car_classes_bp.route('/class/<int:id_class>', methods=['DELETE'])
def delete_class(id_class):
    """Удаление класса автомобилей"""
    car_class = CarClass.query.get(id_class)
    if not car_class:
        return jsonify({'error': 'Класс не найден'}), 404
    
    # Проверка наличия дочерних элементов
    if car_class.children:
        return jsonify({'error': 'Нельзя удалить класс с дочерними элементами'}), 400
    
    # Проверка наличия автомобилей в классе
    if car_class.cars:
        return jsonify({'error': 'Нельзя удалить класс, содержащий автомобили'}), 400
    
    try:
        db.session.delete(car_class)
        db.session.commit()
        return jsonify({'message': 'Класс успешно удален'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@car_classes_bp.route('/class/<int:id_class>/move', methods=['PUT'])
def move_class(id_class):
    """Перемещение класса в другой родительский класс"""
    data = request.get_json()
    new_parent_id = data.get('main_class')
    
    car_class = CarClass.query.get(id_class)
    if not car_class:
        return jsonify({'error': 'Класс не найден'}), 404
    
    if car_class.check_cycle(new_parent_id):
        return jsonify({'error': 'Обнаружен цикл в иерархии'}), 400
    
    car_class.main_class = new_parent_id
    
    try:
        db.session.commit()
        return jsonify(car_class.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@car_classes_bp.route('/class/<int:id_class>/children', methods=['GET'])
def get_children(id_class):
    """Получение дочерних классов"""
    car_class = CarClass.query.get(id_class)
    if not car_class:
        return jsonify({'error': 'Класс не найден'}), 404
    
    children = car_class.get_all_children()
    return jsonify({
        'children': [c.to_dict() for c in children],
        'count': len(children)
    }), 200


@car_classes_bp.route('/class/<int:id_class>/parents', methods=['GET'])
def get_parents(id_class):
    """Получение родительских классов"""
    car_class = CarClass.query.get(id_class)
    if not car_class:
        return jsonify({'error': 'Класс не найден'}), 404
    
    parents = car_class.get_all_parents()
    return jsonify({
        'parents': [p.to_dict() for p in parents],
        'count': len(parents)
    }), 200


@car_classes_bp.route('/class/terminal', methods=['GET'])
def get_terminal_classes():
    """Получение терминальных (листовых) классов"""
    terminal = CarClass.query.filter(
        ~CarClass.id_class.in_(
            db.session.query(CarClass.main_class).filter(CarClass.main_class != None)
        )
    ).all()
    
    return jsonify({
        'classes': [c.to_dict() for c in terminal],
        'count': len(terminal)
    }), 200


@car_classes_bp.route('/class/tree', methods=['GET'])
def get_tree():
    """Получение дерева классов"""
    root = CarClass.query.filter(CarClass.main_class == None).first()
    if not root:
        return jsonify({'error': 'Корневой класс не найден'}), 404
    
    def build_tree(node):
        result = node.to_dict()
        result['children'] = [build_tree(child) for child in node.children]
        return result
    
    return jsonify(build_tree(root)), 200
