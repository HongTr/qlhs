from app import app, db
from models import Student, TuitionPayment
from datetime import datetime, timedelta
import random

def create_sample_data():
    # Xóa dữ liệu cũ
    with app.app_context():
        db.session.query(TuitionPayment).delete()
        db.session.query(Student).delete()
        db.session.commit()
        
        # Danh sách họ phổ biến
        ho = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng"]
        # Danh sách tên đệm nam
        dem_nam = ["Văn", "Hữu", "Đức", "Công", "Quang", "Anh", "Minh"]
        # Danh sách tên đệm nữ
        dem_nu = ["Thị", "Thu", "Ngọc", "Thanh", "Kim", "Hoài"]
        # Danh sách tên
        ten = ["An", "Bình", "Cường", "Dũng", "Em", "Phúc", "Giang", "Hùng", "Linh", "Mai", 
               "Nam", "Oanh", "Phương", "Quân", "Thảo", "Uyên", "Việt", "Xuân", "Yến"]
        
        # Danh sách trường tiểu học
        truong_tieu_hoc = [
            "Tiểu học Lê Quý Đôn",
            "Tiểu học Nguyễn Bỉnh Khiêm",
            "Tiểu học Trưng Vương"
        ]
        
        # Danh sách trường THCS
        truong_thcs = [
            "THCS Nguyễn Huệ",
            "THCS Lê Lợi",
            "THCS Trần Hưng Đạo"
        ]

        # Học phí theo cấp học
        hoc_phi = {
            "Tiểu học": 250000,
            "THCS": 300000
        }

        created_students = []  # Lưu danh sách học sinh để tạo dữ liệu học phí

        # Lấy năm hiện tại
        current_year = datetime.now().year

        # Tạo 50 học sinh mẫu
        for _ in range(50):
            # Random thông tin cơ bản
            gender = random.choice(["Nam", "Nữ"])
            ho_random = random.choice(ho)
            dem_random = random.choice(dem_nam if gender == "Nam" else dem_nu)
            ten_random = random.choice(ten)
            name = f"{ho_random} {dem_random} {ten_random}"
            
            # Random lớp và tuổi phù hợp
            grade = random.randint(1, 9)
            age = grade + 5  # Tuổi = lớp + 5 (ví dụ: lớp 1 -> 6 tuổi)
            birth_year = current_year - age  # Tính năm sinh từ tuổi
            
            # Chọn trường dựa vào lớp
            if grade <= 5:
                school = random.choice(truong_tieu_hoc)
            else:
                school = random.choice(truong_thcs)
            
            # Random địa chỉ
            address = f"Số {random.randint(1, 200)} Đường {random.randint(1, 50)}, Phường {random.randint(1, 20)}"
            
            # Random số điện thoại
            phone = f"09{random.randint(10000000, 99999999)}"
            
            # Tạo ngày bắt đầu học trong khoảng 2 năm gần đây
            days_ago = random.randint(0, 730)  # Random trong 2 năm
            start_date = datetime.now() - timedelta(days=days_ago)
            
            # Tạo học sinh mới
            student = Student(
                name=name,
                gender=gender,
                age=age,
                birth_year=birth_year,
                grade=str(grade),
                school=school,
                address=address,
                phone=phone,
                father_name=f"{ho_random} Văn {random.choice(ten)}",
                father_phone=f"09{random.randint(10000000, 99999999)}",
                mother_name=f"Nguyễn Thị {random.choice(ten)}",
                mother_phone=f"09{random.randint(10000000, 99999999)}",
                start_date=start_date,
                created_at=datetime.now(),
                graduated=False,
                last_grade_update=None
            )
            
            db.session.add(student)
            created_students.append((student, start_date))
        
        # Lưu học sinh để lấy ID
        db.session.commit()
        
        # Tạo dữ liệu học phí
        for student, start_date in created_students:
            # Xác định mức học phí dựa vào cấp học
            cap_hoc = "Tiểu học" if int(student.grade) <= 5 else "THCS"
            muc_hoc_phi = hoc_phi[cap_hoc]
            
            # Tạo dữ liệu học phí từ ngày bắt đầu học đến hiện tại
            current_date = datetime.now()
            payment_date = start_date
            
            while payment_date < current_date:
                # Random xem tháng này có đóng học phí không (90% xác suất đóng)
                if random.random() < 0.9:
                    # Random số tiền đóng (có thể đóng thêm tiền phụ đạo)
                    amount = muc_hoc_phi + random.choice([0, 50000, 100000])
                    
                    # Random ghi chú
                    notes = random.choice([
                        "Học phí tháng",
                        "Học phí + phụ đạo",
                        "Đã đóng đầy đủ",
                        ""
                    ])
                    
                    payment = TuitionPayment(
                        student_id=student.id,
                        month=payment_date.month,
                        year=payment_date.year,
                        amount=amount,
                        paid_date=payment_date + timedelta(days=random.randint(1, 15)),
                        note=notes
                    )
                    db.session.add(payment)
                
                # Chuyển sang tháng tiếp theo
                if payment_date.month == 12:
                    payment_date = datetime(payment_date.year + 1, 1, 1)
                else:
                    # Sử dụng datetime để tránh lỗi ngày không hợp lệ
                    next_month = payment_date.month + 1
                    payment_date = datetime(payment_date.year, next_month, 1)
        
        # Lưu tất cả thay đổi vào database
        db.session.commit()
        print("Đã tạo xong dữ liệu mẫu!")

if __name__ == "__main__":
    create_sample_data() 