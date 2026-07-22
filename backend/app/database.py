import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Lấy đường dẫn thư mục chứa file database.py này
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Nối đường dẫn để file .db luôn nằm cùng chỗ với file database.py
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'warehouse.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)