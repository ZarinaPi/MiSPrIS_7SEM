"""
Модели параметров (parameters, class_parameters, car_parameters, parameter_groups).
"""

from app.models.base import db


class Parameter(db.Model):
    """
    Метакласс параметра: определяет тип, единицу измерения, описание.
    """
    __tablename__ = 'parameters'
    
    id_param = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)  # "WIDTH", "WEIGHT"
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Тип значения: 'numeric', 'integer', 'string', 'datetime', 'enum'
    value_type = db.Column(db.String(20), nullable=False)
    
    # Для числовых параметров: ссылка на единицу измерения (ei)
    unit_id = db.Column(db.Integer, db.ForeignKey('ei.id_ei'))
    unit = db.relationship('Unit')
    
    # Для параметров-перечислений: ссылка на справочник
    enum_id = db.Column(db.Integer, db.ForeignKey('enumerations.id_enum'))
    enumeration = db.relationship('Enumeration', foreign_keys=[enum_id])
    
    def to_dict(self):
        return {
            'id_param': self.id_param,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'value_type': self.value_type,
            'unit': self.unit.to_dict() if self.unit else None,
            'enumeration': self.enumeration.to_dict() if self.enumeration else None
        }


class ClassParameter(db.Model):
    """
    Привязка параметра к классу изделий с настройками.
    Аналог таблицы PAR_CLASS из ТЗ.
    """
    __tablename__ = 'class_parameters'
    
    id_class = db.Column(db.Integer, db.ForeignKey('car_classes.id_class'), primary_key=True)
    id_param = db.Column(db.Integer, db.ForeignKey('parameters.id_param'), primary_key=True)
    
    is_required = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)  # Порядок отображения
    
    # Ограничения для числовых параметров
    min_value = db.Column(db.Float)
    max_value = db.Column(db.Float)
    
    id_group = db.Column(db.Integer, db.ForeignKey('parameter_groups.id_group'), nullable=True)
    
    # Связи
    car_class = db.relationship('CarClass', backref='linked_params')
    parameter = db.relationship('Parameter')
    group = db.relationship('ParameterGroup', backref='class_parameters')
    
    def to_dict(self):
        return {
            'id_class': self.id_class,
            'id_param': self.id_param,
            'param_code': self.parameter.code if self.parameter else None,
            'param_name': self.parameter.name if self.parameter else None,
            'value_type': self.parameter.value_type if self.parameter else None,
            'is_required': self.is_required,
            'sort_order': self.sort_order,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'id_group': self.id_group,
            'group_name': self.group.name if self.group else None,
            'unit': self.parameter.unit.to_dict() if self.parameter and self.parameter.unit else None
        }


class CarParameter(db.Model):
    """
    Значение параметра у конкретного изделия.
    Аналог таблицы PAR_PROD из ТЗ.
    Поддержка разных типов через отдельные поля.
    """
    __tablename__ = 'car_parameters'
    
    id_car = db.Column(db.Integer, db.ForeignKey('cars.id_car'), primary_key=True)
    id_param = db.Column(db.Integer, db.ForeignKey('parameters.id_param'), primary_key=True)
    
    # Поля для разных типов значений (заполняется только одно в зависимости от типа)
    val_r = db.Column(db.Float)           # VAL_R - вещественные числа
    val_int = db.Column(db.Integer)       # VAL_INT - целые числа
    val_str = db.Column(db.String(255))   # VAL_STR - строки
    val_datetime = db.Column(db.DateTime) # VAL_DATETIME - даты
    enum_val = db.Column(db.Integer, db.ForeignKey('enum_values.id_value'))
    
    enum_value = db.relationship('EnumValue', foreign_keys=[enum_val])
    parameter = db.relationship('Parameter')
    
    def _get_value(self):
        """Вспомогательный метод: возвращает значение в нужном формате"""
        if not self.parameter:
            return None
        vt = self.parameter.value_type
        if vt == 'numeric':
            return self.val_r
        elif vt == 'integer':
            return self.val_int
        elif vt == 'string':
            return self.val_str
        elif vt == 'datetime':
            return self.val_datetime.isoformat() if self.val_datetime else None
        elif vt == 'enum' and self.enum_value:
            return self.enum_value.to_dict()
        return None
    
    def to_dict(self):
        return {
            'id_param': self.id_param,
            'code': self.parameter.code if self.parameter else None,
            'name': self.parameter.name if self.parameter else None,
            'value_type': self.parameter.value_type if self.parameter else None,
            'value': self._get_value(),
            'unit': self.parameter.unit.to_dict() if self.parameter and self.parameter.unit else None
        }


class ParameterGroup(db.Model):
    """Группа параметров (агрегат) для визуального объединения характеристик в карточке"""
    __tablename__ = 'parameter_groups'
    
    id_group = db.Column(db.Integer, primary_key=True)
    id_class = db.Column(db.Integer, db.ForeignKey('car_classes.id_class'), nullable=True)  # NULL = глобальная группа
    name = db.Column(db.String(100), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    
    car_class = db.relationship('CarClass', backref='parameter_groups')


# Импорт зависимостей
from app.models.unit import Unit
from app.models.enumeration import Enumeration, EnumValue
from app.models.car_class import CarClass
