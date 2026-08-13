"""
Flask приложение для управления классификатором автомобилей и хозяйственных операций.
Модульная структура проекта.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

# Инициализация расширений
db = SQLAlchemy()


def create_app(config_object=None):
    """Фабрика приложения с поддержкой конфигурации."""
    app = Flask(__name__)
    
    # Конфигурация
    if config_object:
        app.config.from_object(config_object)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = 'dev-key-change-in-production'
    
    # Инициализация расширений
    db.init_app(app)
    CORS(app)
    
    # Регистрация blueprint (blueprints)
    from app.api.car_classes import car_classes_bp
    from app.api.cars import cars_bp
    from app.api.enumerations import enumerations_bp
    from app.api.units import units_bp
    from app.api.parameters import parameters_bp
    from app.api.ho import ho_bp
    
    app.register_blueprint(car_classes_bp, url_prefix='/api')
    app.register_blueprint(cars_bp, url_prefix='/api')
    app.register_blueprint(enumerations_bp, url_prefix='/api')
    app.register_blueprint(units_bp, url_prefix='/api')
    app.register_blueprint(parameters_bp, url_prefix='/api')
    app.register_blueprint(ho_bp, url_prefix='/api')
    
    # Создание таблиц БД при первом запуске
    with app.app_context():
        db.create_all()
        
        # Инициализация тестовыми данными
        from app.models.unit import Unit
        from app.models.car_class import CarClass
        
        if not Unit.query.first():
            db.session.add(Unit(short_name='шт', name='штуки'))
            db.session.commit()
        
        if not CarClass.query.first():
            root = CarClass(name='Каталог Каршеринга', short_name='ROOT')
            db.session.add(root)
            db.session.commit()
            print('База данных создана и заполнена тестовыми данными!')
    
    return app
