"""
Модели хозяйственных операций (HO).
"""

from app.models.base import db
from datetime import datetime


class EconomicEntity(db.Model):
    """Субъект хозяйственной деятельности"""
    __tablename__ = 'economic_entities'
    
    id_sxd = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    inn = db.Column(db.String(12), unique=True)
    entity_type = db.Column(db.String(20))  # 'legal', 'individual', 'department'
    
    def to_dict(self):
        return {
            'id_sxd': self.id_sxd,
            'name': self.name,
            'inn': self.inn,
            'entity_type': self.entity_type
        }


class HOClass(db.Model):
    """Классификатор хозяйственных операций"""
    __tablename__ = 'ho_classes'
    
    id_ho_class = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('ho_classes.id_ho_class'))
    
    parent = db.relationship('HOClass', backref='children', remote_side=[id_ho_class])
    
    def to_dict(self):
        return {
            'id_ho_class': self.id_ho_class,
            'name': self.name,
            'code': self.code,
            'parent_id': self.parent_id
        }


class Role(db.Model):
    """Роль в хозяйственной операции"""
    __tablename__ = 'roles'
    
    id_role = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # "Отправитель", "Плательщик"
    code = db.Column(db.String(20), unique=True)
    
    def to_dict(self):
        return {'id_role': self.id_role, 'name': self.name, 'code': self.code}


class HOClassRole(db.Model):
    """Привязка роли к типу хозяйственной операции"""
    __tablename__ = 'ho_class_roles'
    
    id_ho_class = db.Column(db.Integer, db.ForeignKey('ho_classes.id_ho_class'), primary_key=True)
    id_role = db.Column(db.Integer, db.ForeignKey('roles.id_role'), primary_key=True)
    is_required = db.Column(db.Boolean, default=True)
    
    ho_class = db.relationship('HOClass', backref='allowed_roles')
    role = db.relationship('Role')


class HOParameter(db.Model):
    """Параметр хозяйственной операции (метакласс)"""
    __tablename__ = 'ho_parameters'
    
    id_param = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    value_type = db.Column(db.String(20), nullable=False)  # numeric, integer, string, datetime, enum
    unit_id = db.Column(db.Integer, db.ForeignKey('ei.id_ei'))
    enum_id = db.Column(db.Integer, db.ForeignKey('enumerations.id_enum'))
    
    def to_dict(self):
        return {
            'id_param': self.id_param,
            'code': self.code,
            'name': self.name,
            'value_type': self.value_type
        }


class HOClassParameter(db.Model):
    """Привязка параметра к типу хозяйственной операции"""
    __tablename__ = 'ho_class_parameters'
    
    id_ho_class = db.Column(db.Integer, db.ForeignKey('ho_classes.id_ho_class'), primary_key=True)
    id_param = db.Column(db.Integer, db.ForeignKey('ho_parameters.id_param'), primary_key=True)
    sort_order = db.Column(db.Integer, default=0)
    min_value = db.Column(db.Float)
    max_value = db.Column(db.Float)
    is_required = db.Column(db.Boolean, default=False)


class HOInstance(db.Model):
    """Экземпляр хозяйственной операции"""
    __tablename__ = 'ho_instances'
    
    id_ho = db.Column(db.Integer, primary_key=True)
    id_ho_class = db.Column(db.Integer, db.ForeignKey('ho_classes.id_ho_class'), nullable=False)
    doc_number = db.Column(db.String(50))
    doc_date = db.Column(db.Date)
    total_amount = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    ho_class = db.relationship('HOClass')
    
    def to_dict(self):
        return {
            'id_ho': self.id_ho,
            'ho_class': self.ho_class.to_dict(),
            'doc_number': self.doc_number,
            'doc_date': self.doc_date.isoformat() if self.doc_date else None,
            'total_amount': self.total_amount,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class HOActor(db.Model):
    """Участник хозяйственной операции (роль + субъект)"""
    __tablename__ = 'ho_actors'
    
    id_ho = db.Column(db.Integer, db.ForeignKey('ho_instances.id_ho'), primary_key=True)
    id_role = db.Column(db.Integer, db.ForeignKey('roles.id_role'), primary_key=True)
    id_sxd = db.Column(db.Integer, db.ForeignKey('economic_entities.id_sxd'), nullable=False)
    
    sxd = db.relationship('EconomicEntity')
    role = db.relationship('Role')


class HOParameterValue(db.Model):
    """Значение параметра у экземпляра хозяйственной операции"""
    __tablename__ = 'ho_parameter_values'
    
    id_ho = db.Column(db.Integer, db.ForeignKey('ho_instances.id_ho'), primary_key=True)
    id_param = db.Column(db.Integer, db.ForeignKey('ho_parameters.id_param'), primary_key=True)
    val_r = db.Column(db.Float)
    val_int = db.Column(db.Integer)
    val_str = db.Column(db.String(255))
    val_datetime = db.Column(db.DateTime)
    enum_val = db.Column(db.Integer, db.ForeignKey('enum_values.id_value'))
    
    enum_value = db.relationship('EnumValue', foreign_keys=[enum_val])


class HOPosition(db.Model):
    """Позиция в хозяйственной операции (товары/услуги)"""
    __tablename__ = 'ho_positions'
    
    id_position = db.Column(db.Integer, primary_key=True)
    id_ho = db.Column(db.Integer, db.ForeignKey('ho_instances.id_ho'), nullable=False)
    id_car = db.Column(db.Integer, db.ForeignKey('cars.id_car'))
    quantity = db.Column(db.Float, default=1.0)
    price = db.Column(db.Float)
    amount = db.Column(db.Float)
    
    ho = db.relationship('HOInstance', backref='positions')
    car = db.relationship('Car')


# Импорт зависимостей
from app.models.unit import Unit
from app.models.enumeration import EnumValue
from app.models.car import Car
