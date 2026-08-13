"""
Модель автомобиля (cars).
"""

from app.models.base import db


class Car(db.Model):
    """Конкретные автомобили (таблица cars)"""
    __tablename__ = 'cars'
    
    id_car = db.Column(db.Integer, primary_key=True)
    short_name = db.Column(db.String(20), unique=True, nullable=False)
    id_class = db.Column(db.Integer, db.ForeignKey('car_classes.id_class'), nullable=False)
    
    car_class = db.relationship('CarClass', backref='cars')
    
    def to_dict(self):
        attrs = {a.enum.name: a.value_obj.value for a in self.attributes}
        
        return {
            'id_car': self.id_car,
            'short_name': self.short_name,
            'name': self.car_class.name,
            'id_class': self.id_class,
            'attributes': attrs
        }
