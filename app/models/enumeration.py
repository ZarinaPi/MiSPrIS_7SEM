"""
Модели перечислений (enumerations, enum_values, class_enums, car_enum_values).
"""

from app.models.base import db


class Enumeration(db.Model):
    """Справочник-перечисление (CHEM_CLASS)"""
    __tablename__ = 'enumerations'
    
    id_enum = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    value_type = db.Column(db.String(20), default='string')  # string, numeric, icon
    
    # Связи
    values = db.relationship('EnumValue', backref='enumeration', lazy='select', cascade='all, delete-orphan')
    linked_classes = db.relationship('ClassEnum', backref='enumeration', lazy='select')
    
    def to_dict(self):
        return {
            'id_enum': self.id_enum,
            'name': self.name,
            'description': self.description,
            'value_type': self.value_type
        }


class EnumValue(db.Model):
    """Значение перечисления (POS_ENUM)"""
    __tablename__ = 'enum_values'
    
    id_value = db.Column(db.Integer, primary_key=True)
    id_enum = db.Column(db.Integer, db.ForeignKey('enumerations.id_enum'), nullable=False)
    value = db.Column(db.String(100), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    numeric_value = db.Column(db.Float)
    icon_url = db.Column(db.String(255))
    unit_id = db.Column(db.Integer, db.ForeignKey('ei.id_ei'))
    
    unit = db.relationship('Unit')
    
    def to_dict(self):
        return {
            'id_value': self.id_value,
            'value': self.value,
            'sort_order': self.sort_order,
            'numeric_value': self.numeric_value,
            'icon_url': self.icon_url,
            'unit': self.unit.to_dict() if self.unit else None
        }


class ClassEnum(db.Model):
    """Привязка перечисления к классу автомобилей"""
    __tablename__ = 'class_enums'
    
    id_class = db.Column(db.Integer, db.ForeignKey('car_classes.id_class'), primary_key=True)
    id_enum = db.Column(db.Integer, db.ForeignKey('enumerations.id_enum'), primary_key=True)
    is_required = db.Column(db.Boolean, default=False)
    
    car_class = db.relationship('CarClass', backref=db.backref('linked_enums', lazy='select'))


class CarEnumValue(db.Model):
    """Выбранное значение характеристики у конкретной машины"""
    __tablename__ = 'car_enum_values'
    
    id_car = db.Column(db.Integer, db.ForeignKey('cars.id_car'), primary_key=True)
    id_enum = db.Column(db.Integer, db.ForeignKey('enumerations.id_enum'), primary_key=True)
    id_value = db.Column(db.Integer, db.ForeignKey('enum_values.id_value'), nullable=False)
    
    car = db.relationship('Car', backref=db.backref('attributes', lazy='select'))
    enum = db.relationship('Enumeration')
    value_obj = db.relationship('EnumValue')
    
    def to_dict(self):
        return {
            'id_enum': self.id_enum,
            'enum_name': self.enum.name,
            'id_value': self.id_value,
            'value': self.value_obj.value,
            'sort_order': self.value_obj.sort_order
        }


# Импорт Unit для связи
from app.models.unit import Unit
