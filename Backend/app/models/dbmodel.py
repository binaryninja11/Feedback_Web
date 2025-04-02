from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
import json

Base = declarative_base()

class Students(Base):
    __tablename__ = "category"
    stdid = Column(String(7), primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    last_name = Column(Integer, ForeignKey("image_main.id", onupdate="CASCADE"), index=True, nullable=True)
    password = Column(String, index=True, nullable=True)
    level = Column(String,index=True, nullable=True)
    major = Column(String, index=True, nullable=True)
    active = Column(String, index=True, nullable=True)

    # Explicitly use main_image_id for the one-to-one relationship
    main_image = relationship("Image_main", uselist=False, foreign_keys=[main_image_id])
    # One-to-many relationship for additional images
    images = relationship("Image", back_populates="category", cascade="all, delete-orphan")


class Image(Base):
    __tablename__ = "image"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=True)
    name_base64 = Column(String, unique=True, index=True, nullable=False)
    category_id = Column(Integer, ForeignKey("category.id", ondelete="CASCADE", onupdate="CASCADE"), index=True, nullable=False)

    # Inverse relationship for additional images
    category = relationship("Category", back_populates="images")


class Image_main(Base):
    __tablename__ = "image_main"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=True)
    name_base64 = Column(String, unique=True, index=True, nullable=False)
    category_id = Column(Integer, ForeignKey("category.id", ondelete="CASCADE", onupdate="CASCADE"), index=True, nullable=False)

    # A separate relationship (if needed) to access the owning category
    owner = relationship("Category", foreign_keys=[category_id])