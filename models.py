from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(2), nullable=False)
    school = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(15))
    father_name = db.Column(db.String(100))
    father_phone = db.Column(db.String(15))
    mother_name = db.Column(db.String(100))
    mother_phone = db.Column(db.String(15))
    # Thêm relationship với TuitionPayment
    tuition_payments = db.relationship('TuitionPayment', backref='student', lazy=True, cascade="all, delete-orphan")

class TuitionPayment(db.Model):
    __tablename__ = 'tuition_payments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # Tháng (1-12)
    year = db.Column(db.Integer, nullable=False)   # Năm
    amount = db.Column(db.Float, nullable=False)   # Số tiền
    paid_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Ngày nộp
    note = db.Column(db.String(200))  # Ghi chú
    
    __table_args__ = (
        db.UniqueConstraint('student_id', 'month', 'year', name='unique_payment_per_month'),
    )
