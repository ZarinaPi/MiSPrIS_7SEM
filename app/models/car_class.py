"""
Модель класса автомобилей (car_classes).
"""

from app.models.base import db


class CarClass(db.Model):
    """Метакласс для иерархии классификатора (таблица car_classes)"""
    __tablename__ = 'car_classes'
    
    id_class = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(50))
    base_ei = db.Column(db.Integer, db.ForeignKey('ei.id_ei'))
    main_class = db.Column(db.Integer, db.ForeignKey('car_classes.id_class'))
    
    # Рефлексивная связь (родитель → потомки)
    parent = db.relationship('CarClass', 
                             backref=db.backref('children', lazy='select'),
                             remote_side=[id_class])
    
    def to_dict(self):
        return {
            'id_class': self.id_class,
            'name': self.name,
            'short_name': self.short_name,
            'base_ei': self.base_ei,
            'main_class': self.main_class
        }
    
    def check_cycle(self, new_parent_id):
        """Проверка на циклы при смене родителя"""
        if new_parent_id == self.id_class:
            return True
        current = CarClass.query.get(new_parent_id)
        while current:
            if current.id_class == self.id_class:
                return True
            current = current.parent
        return False
    
    def get_all_children(self):
        """Рекурсивно найти всех потомков"""
        result = list(self.children)
        for child in self.children:
            result.extend(child.get_all_children())
        return result
    
    def get_all_parents(self):
        """Найти всех предков"""
        result = []
        current = self.parent
        while current:
            result.append(current)
            current = current.parent
        return result
