"""
Модель единицы измерения (ei).
"""

from app.models.base import db


class Unit(db.Model):
    """Единицы измерения (таблица ei)"""
    __tablename__ = 'ei'
    
    id_ei = db.Column(db.Integer, primary_key=True)
    short_name = db.Column(db.String(10), nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False)
    
    def to_dict(self):
        return {
            'id_ei': self.id_ei,
            'short_name': self.short_name,
            'name': self.name
        }
