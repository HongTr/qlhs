from app import app, db
from models import Student, TuitionPayment
import random
from datetime import datetime, timedelta
import sys
from sqlalchemy.exc import SQLAlchemyError

# Danh sách họ phổ biến
ho = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]

# Danh sách tên đệm và tên cho Nam
ten_dem_nam = ["Văn", "Đức", "Minh", "Hoàng", "Thành", "Công", "Hữu", "Quang", "Anh", "Đình"]
ten_nam = ["An", "Bình", "Cường", "Dũng", "Hùng", "Nam", "Phúc", "Quân", "Tùng", "Minh", 
           "Long", "Khang", "Phong", "Kiên", "Đạt", "Thịnh", "Trung", "Việt", "Khải", "Đức"]

# Danh sách tên đệm và tên cho Nữ
ten_dem_nu = ["Thị", "Thu", "Thanh", "Kim", "Ngọc", "Hoàng", "Thùy", "Phương", "Thúy", "Mai"]
ten_nu = ["Anh", "Linh", "Phương", "Thảo", "Uyên", "Mai", "Hương", "Ngọc", "Trang", "Hà",
          "Lan", "Chi", "Hạnh", "Yến", "Nhung", "Dung", "Nga", "Thủy", "Hồng", "Vân"]

# Danh sách trường tiểu học
truong_tieu_hoc = [
    "Trường Tiểu học Lê Lợi",
    "Trường Tiểu học Nguyễn Huệ",
    "Trường Tiểu học Trưng Vương",
    "Trường Tiểu học Quang Trung",
    "Trường Tiểu học Lê Quý Đôn"
]

# Danh sách trường THCS
truong_thcs = [
    "Trường THCS Lý Tự Trọng",
    "Trường THCS Nguyễn Trãi",
    "Trường THCS Trần Phú",
    "Trường THCS Lê Hồng Phong",
    "Trường THCS Ngô Sĩ Liên"
]

# Danh sách quận/huyện và phường/xã
quan_huyen = ["Quận 1", "Quận 3", "Quận 4", "Quận 5", "Quận 10", "Quận Bình Thạnh", "Quận Phú Nhuận"]
phuong_xa = ["Phường 1", "Phường 2", "Phường 3", "Phường 4", "Phường 5", "Phường 6", "Phường 7"]

def tao_ten(gioi_tinh):
    """Tạo họ và tên ngẫu nhiên dựa trên giới tính"""
    ho_random = random.choice(ho)
    if gioi_tinh == "Nam":
        ten_dem_random = random.choice(ten_dem_nam)
        ten_random = random.choice(ten_nam)
    else:
        ten_dem_random = random.choice(ten_dem_nu)
        ten_random = random.choice(ten_nu)
    return f"{ho_random} {ten_dem_random} {ten_random}"

def tao_so_dien_thoai():
    """Tạo số điện thoại Việt Nam ngẫu nhiên"""
    dau_so = random.choice(['086', '096', '097', '098', '032', '033', '034', '035', '036', '037', '038', '039'])
    duoi = ''.join([str(random.randint(0, 9)) for _ in range(7)])
    return f"{dau_so}{duoi}"

def tao_dia_chi():
    """Tạo địa chỉ ngẫu nhiên"""
    return f"Số {random.randint(1, 200)}, Đường {random.randint(1, 50)}, {random.choice(phuong_xa)}, {random.choice(quan_huyen)}, TP.HCM"

def lay_tuoi_theo_lop(lop):
    """Lấy tuổi phù hợp theo lớp"""
    return lop + 5  # Ví dụ: Lớp 1 -> 6 tuổi, Lớp 2 -> 7 tuổi, ...

def lay_truong_theo_lop(lop):
    """Lấy trường phù hợp theo cấp học"""
    if 1 <= lop <= 5:  # Tiểu học
        return random.choice(truong_tieu_hoc)
    else:  # THCS
        return random.choice(truong_thcs)

def tao_hoc_phi():
    """Tạo số tiền học phí ngẫu nhiên"""
    return random.choice([250000, 300000, 350000, 400000])

def kiem_tra_database():
    """Kiểm tra xem database đã tồn tại và có thể kết nối được không"""
    try:
        with app.app_context():
            # Thử query một bảng
            Student.query.first()
            return True
    except Exception as e:
        print(f"Lỗi khi kiểm tra database: {str(e)}")
        return False

def them_du_lieu_mau():
    if not kiem_tra_database():
        print("Không thể kết nối đến database. Hãy chắc chắn rằng:")
        print("1. Database đã được tạo")
        print("2. Các bảng đã được tạo (chạy 'flask db upgrade')")
        print("3. Có quyền truy cập vào database")
        return

    try:
        with app.app_context():
            print("Bắt đầu tạo dữ liệu mẫu...")
            
            # Xóa dữ liệu cũ
            print("Đang xóa dữ liệu cũ...")
            TuitionPayment.query.delete()
            Student.query.delete()
            db.session.commit()
            print("Đã xóa dữ liệu cũ thành công!")
            
            # Thêm học sinh mới
            print("Đang tạo dữ liệu học sinh mới...")
            students_created = 0
            payments_created = 0
            
            for i in range(50):  # Tạo 50 học sinh
                try:
                    # Tạo thông tin cơ bản
                    lop = random.randint(1, 9)
                    gioi_tinh = random.choice(["Nam", "Nữ"])
                    
                    hoc_sinh = Student(
                        name=tao_ten(gioi_tinh),
                        gender=gioi_tinh,
                        age=lay_tuoi_theo_lop(lop),
                        grade=str(lop),
                        school=lay_truong_theo_lop(lop),
                        address=tao_dia_chi(),
                        phone=tao_so_dien_thoai(),
                        father_name=tao_ten("Nam"),
                        father_phone=tao_so_dien_thoai(),
                        mother_name=tao_ten("Nữ"),
                        mother_phone=tao_so_dien_thoai()
                    )
                    db.session.add(hoc_sinh)
                    db.session.commit()
                    students_created += 1
                    
                    # Thêm dữ liệu học phí
                    current_date = datetime.now()
                    months_paid = []
                    
                    for month_offset in range(3):
                        if random.random() < 0.7:
                            payment_date = current_date - timedelta(days=month_offset*30)
                            month = payment_date.month
                            year = payment_date.year
                            
                            if (month, year) not in months_paid:
                                months_paid.append((month, year))
                                hoc_phi = TuitionPayment(
                                    student_id=hoc_sinh.id,
                                    month=month,
                                    year=year,
                                    amount=tao_hoc_phi(),
                                    paid_date=payment_date,
                                    note=f"Học phí tháng {month}/{year}"
                                )
                                db.session.add(hoc_phi)
                                db.session.commit()
                                payments_created += 1
                    
                    # In tiến độ
                    print(f"Đã tạo {students_created}/50 học sinh và {payments_created} bản ghi học phí", end='\r')
                    
                except SQLAlchemyError as e:
                    print(f"\nLỗi khi tạo học sinh thứ {i+1}: {str(e)}")
                    db.session.rollback()
                    continue
            
            print(f"\nHoàn thành! Đã tạo:")
            print(f"- {students_created} học sinh")
            print(f"- {payments_created} bản ghi học phí")
            
    except Exception as e:
        print(f"Lỗi không mong muốn: {str(e)}")
        db.session.rollback()
        sys.exit(1)
    finally:
        db.session.close()

if __name__ == "__main__":
    them_du_lieu_mau() 