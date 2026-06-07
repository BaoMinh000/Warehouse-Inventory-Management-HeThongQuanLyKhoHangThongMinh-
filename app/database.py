# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./warehouse.db"

# engine chịu trách nhiệm quản lý kết nối vật lý tới file CSDL
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Khởi tạo lớp tạo Session để các API gọi vào đóng/mở giao dịch với DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)