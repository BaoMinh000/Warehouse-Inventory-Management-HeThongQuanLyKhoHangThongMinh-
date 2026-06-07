# app/models/schemas.py
from pydantic import BaseModel, Field

class ProductCreateSchema(BaseModel):
    barcode: str = Field(..., description="Mã vạch duy nhất của sản phẩm")
    product_name: str = Field(..., description="Tên sản phẩm")
    strategy_type: str = Field(..., description="Chiến lược xuất kho: 'FIFO' hoặc 'LIFO'")

    class Config:
        from_attributes = True

class StockInSchema(BaseModel):
    barcode: str = Field(..., description="Mã vạch sản phẩm nhập kho")
    quantity: int = Field(..., gt=0, description="Số lượng nhập kho, phải lớn hơn 0")
    expiry_date: str = Field(..., description="Hạn sử dụng (Định dạng: YYYY-MM-DD)")

    class Config:
        from_attributes = True

class StockOutSchema(BaseModel):
    barcode: str = Field(..., description="Mã vạch sản phẩm xuất kho")
    quantity: int = Field(..., gt=0, description="Số lượng cần xuất, phải lớn hơn 0")

    class Config:
        from_attributes = True