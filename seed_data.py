from app import app, db
from models import Student
import random

# Danh sách họ phổ biến
ho = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng"]

# Danh sách tên đệm và tên
ten_dem = ["Văn", "Thị", "Đức", "Minh", "Hoàng", "Thành", "Thanh", "Công", "Kim", "Thu"]
ten = ["An", "Bình", "Cường", "Dũng", "Em", "Phúc", "Giang", "Hùng", "Linh", "Mai",
       "Nam", "Oanh", "Phương", "Quân", "Thảo", "Uyên", "Việt", "Xuân", "Yến", "Hoa"]

# Danh sách trường học
truong_hoc = [
    "Trường Tiểu học Lê Lợi",
    "Trường Tiểu học Nguyễn Huệ",
    "Trường Tiểu học Trưng Vương",
    "Trường Tiểu học Quang Trung",
    "Trường Tiểu học Lê Quý Đôn"
]

def tao_ten():
    """Tạo họ và tên ngẫu nhiên"""
    return f"{random.choice(ho)} {random.choice(ten_dem)} {random.choice(ten)}"

def tao_so_dien_thoai():
    """Tạo số điện thoại ngẫu nhiên"""
    return f"0{random.randint(3, 9)}{random.randint(10000000, 99999999)}"

def them_du_lieu_mau():
    with app.app_context():
        # Xóa dữ liệu cũ
        Student.query.delete()
        db.session.commit()
        
        # Thêm học sinh mới
        for _ in range(50):  # Tạo 50 học sinh
            hoc_sinh = Student(
                name=tao_ten(),
                gender=random.choice(["Nam", "Nữ"]),
                age=random.randint(6, 15),
                grade=str(random.randint(1, 9)),
                school=random.choice(truong_hoc),
                address=f"Số {random.randint(1, 200)}, Đường {random.randint(1, 50)}, Phường {random.randint(1, 20)}",
                phone=tao_so_dien_thoai(),
                father_name=tao_ten(),
                father_phone=tao_so_dien_thoai(),
                mother_name=tao_ten(),
                mother_phone=tao_so_dien_thoai()
            )
            db.session.add(hoc_sinh)
        
        # Lưu vào database
        db.session.commit()
        print("Đã thêm dữ liệu mẫu thành công!")

if __name__ == "__main__":
    them_du_lieu_mau() 