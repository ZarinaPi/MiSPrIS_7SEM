"""
Модели данных приложения.
"""

from app.models.base import db

# Импорт моделей для регистрации в SQLAlchemy
from app.models.unit import Unit
from app.models.car_class import CarClass
from app.models.car import Car
from app.models.enumeration import Enumeration, EnumValue, ClassEnum, CarEnumValue
from app.models.parameter import Parameter, ClassParameter, CarParameter, ParameterGroup
from app.models.ho import (
    EconomicEntity, HOClass, Role, HOClassRole, HOParameter,
    HOClassParameter, HOInstance, HOActor, HOParameterValue, HOPosition
)

__all__ = [
    'db',
    'Unit',
    'CarClass',
    'Car',
    'Enumeration',
    'EnumValue',
    'ClassEnum',
    'CarEnumValue',
    'Parameter',
    'ClassParameter',
    'CarParameter',
    'ParameterGroup',
    'EconomicEntity',
    'HOClass',
    'Role',
    'HOClassRole',
    'HOParameter',
    'HOClassParameter',
    'HOInstance',
    'HOActor',
    'HOParameterValue',
    'HOPosition'
]
