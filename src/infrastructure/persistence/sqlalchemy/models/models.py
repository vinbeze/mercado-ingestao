from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class DocumentRawModel(Base):
    __tablename__ = "documents_raw"

    id = Column(Integer, primary_key=True, autoincrement=True)
    image_reference = Column(String(500), nullable=False)
    qr_url = Column(Text, nullable=False)
    html = Column(Text, nullable=False)
    status = Column(String(50), nullable=False)


class PurchaseReceiptModel(Base):
    __tablename__ = "purchase_receipts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_name = Column(String(255), nullable=True)
    store_document = Column(String(20), nullable=True)
    purchase_date = Column(String(30), nullable=True)
    total_amount = Column(Numeric(10, 2), nullable=True)
    receipt_number = Column(String(50), nullable=True)

    items = relationship("PurchaseItemNormalizedModel", back_populates="receipt")


class PurchaseItemNormalizedModel(Base):
    __tablename__ = "purchase_items_normalized"

    id = Column(Integer, primary_key=True, autoincrement=True)
    receipt_id = Column(Integer, ForeignKey("purchase_receipts.id"), nullable=False)
    canonical_name = Column(String(255), nullable=False)
    brand = Column(String(100), nullable=True)
    category = Column(String(100), nullable=True)
    quantity = Column(Numeric(10, 3), nullable=True)
    unit = Column(String(20), nullable=True)
    unit_price = Column(Numeric(10, 2), nullable=True)
    total_price = Column(Numeric(10, 2), nullable=True)

    receipt = relationship("PurchaseReceiptModel", back_populates="items")
