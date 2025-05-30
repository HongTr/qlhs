from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, Student, TuitionPayment   # <-- import từ models.py
import os
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__, instance_relative_config=True)

# Đảm bảo instance folder tồn tại
os.makedirs(app.instance_path, exist_ok=True)

# Cấu hình database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'student.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Thêm secret key cho flash messages

# Số học sinh trên mỗi trang
STUDENTS_PER_PAGE = 10

# Khởi tạo db
db.init_app(app)
migrate = Migrate(app, db)

# Tạo database nếu chưa có
with app.app_context():
    db.create_all()

def get_all_grades():
    """Trả về danh sách các lớp từ 1-9"""
    return list(range(1, 10))

@app.route('/')
def index():
    # Lấy số trang từ query parameter, mặc định là trang 1
    page = request.args.get('page', 1, type=int)
    
    # Lấy tất cả các lớp từ 1-9
    all_grades = get_all_grades()
    
    # Lấy danh sách tất cả các trường học đã có trong database
    schools = db.session.query(Student.school).distinct().order_by(Student.school).all()
    schools = [school[0] for school in schools]
    
    # Lấy các tham số filter
    selected_grade = request.args.get('grade')
    selected_school = request.args.get('school')
    
    # Xây dựng query
    query = Student.query
    
    # Áp dụng các filter
    if selected_grade and selected_grade.isdigit():
        query = query.filter_by(grade=selected_grade)
    if selected_school:
        query = query.filter_by(school=selected_school)
    
    # Thực hiện phân trang
    pagination = query.order_by(Student.name).paginate(
        page=page,
        per_page=STUDENTS_PER_PAGE,
        error_out=False
    )
    
    # Lấy danh sách học sinh của trang hiện tại
    students = pagination.items
    
    return render_template('index.html', 
                         students=students,
                         pagination=pagination,
                         grades=all_grades,
                         schools=schools,
                         selected_grade=selected_grade,
                         selected_school=selected_school)

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        new_student = Student(
            name=request.form['name'],
            gender=request.form['gender'],
            age=request.form['age'],
            grade=request.form['grade'],
            school=request.form['school'],
            address=request.form['address'],
            phone=request.form['phone'],
            father_name=request.form['father_name'],
            father_phone=request.form['father_phone'],
            mother_name=request.form['mother_name'],
            mother_phone=request.form['mother_phone'],
        )
        db.session.add(new_student)
        db.session.commit()
        flash('Thêm học sinh thành công!')
        return redirect(url_for('index'))
    
    return render_template('add.html', grades=get_all_grades())

@app.route('/delete/<int:id>', methods=['POST'])
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Đã xóa học sinh thành công!')
    return redirect(url_for('index'))

@app.route('/student/<int:id>')
def student_detail(id):
    student = Student.query.get_or_404(id)
    return render_template('detail.html', student=student)

@app.route('/student/<int:id>/edit', methods=['GET', 'POST'])
def edit_student(id):
    student = Student.query.get_or_404(id)
    
    if request.method == 'POST':
        # Cập nhật thông tin học sinh
        student.name = request.form['name']
        student.gender = request.form['gender']
        student.age = request.form['age']
        student.grade = request.form['grade']
        student.school = request.form['school']
        student.address = request.form['address']
        student.phone = request.form['phone']
        student.father_name = request.form['father_name']
        student.father_phone = request.form['father_phone']
        student.mother_name = request.form['mother_name']
        student.mother_phone = request.form['mother_phone']
        
        try:
            db.session.commit()
            flash('Cập nhật thông tin học sinh thành công!')
            return redirect(url_for('student_detail', id=student.id))
        except:
            db.session.rollback()
            flash('Có lỗi xảy ra khi cập nhật thông tin!', 'error')
    
    return render_template('edit.html', student=student, grades=get_all_grades())

@app.route('/student/<int:id>/tuition')
@app.route('/student/<int:id>/tuition/<int:year>')
def tuition_calendar(id, year=None):
    student = Student.query.get_or_404(id)
    
    # Nếu không có năm được chọn, lấy năm hiện tại
    if year is None:
        year = datetime.now().year
    
    # Lấy tất cả các khoản thanh toán của học sinh trong năm được chọn
    payments = TuitionPayment.query.filter_by(
        student_id=id,
        year=year
    ).all()
    
    # Tạo dictionary để dễ dàng kiểm tra tháng nào đã nộp
    paid_months = {payment.month: payment for payment in payments}
    
    return render_template('tuition_calendar.html', 
                         student=student,
                         current_year=year,
                         paid_months=paid_months)

@app.route('/student/<int:id>/tuition/toggle', methods=['POST'])
def toggle_tuition_payment(id):
    try:
        data = request.get_json()
        month = int(data.get('month'))
        year = int(data.get('year'))
        amount = float(data.get('amount', 0))
        note = data.get('note', '')

        # Validate input
        if not all([isinstance(month, int), isinstance(year, int)]):
            return jsonify({
                'status': 'error',
                'message': 'Tháng và năm không hợp lệ'
            }), 400

        if amount < 0:
            return jsonify({
                'status': 'error',
                'message': 'Số tiền không thể âm'
            }), 400

        student = Student.query.get_or_404(id)
        payment = TuitionPayment.query.filter_by(
            student_id=id,
            month=month,
            year=year
        ).first()

        if payment:
            if amount > 0:  # Cập nhật thông tin thanh toán
                payment.amount = amount
                payment.note = note
                payment.paid_date = datetime.utcnow()
                message = 'Đã cập nhật thông tin thanh toán'
            else:  # Xóa thanh toán
                db.session.delete(payment)
                message = 'Đã xóa thông tin thanh toán'
        else:
            if amount > 0:  # Thêm thanh toán mới
                payment = TuitionPayment(
                    student_id=id,
                    month=month,
                    year=year,
                    amount=amount,
                    note=note,
                    paid_date=datetime.utcnow()
                )
                db.session.add(payment)
                message = 'Đã thêm thông tin thanh toán'
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Vui lòng nhập số tiền'
                }), 400

        db.session.commit()
        
        # Return detailed payment info for UI update
        if amount > 0:
            return jsonify({
                'status': 'success',
                'message': message,
                'data': {
                    'amount': "{:,.0f}".format(amount),
                    'paid_date': datetime.utcnow().strftime('%d/%m/%Y'),
                    'note': note
                }
            })
        else:
            return jsonify({
                'status': 'success',
                'message': message
            })

    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': 'Dữ liệu không hợp lệ: ' + str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Có lỗi xảy ra: ' + str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
