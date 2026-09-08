from sqlalchemy import Column, ForeignKey, Integer, String, Text, JSON

from app.db import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    display_name = Column(String, nullable=False)
    description = Column(Text, nullable=False)


class CategoryQuestion(Base):
    __tablename__ = "category_questions"

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    question_key = Column(String, nullable=False)
    question_text = Column(String, nullable=False)
    answer_type = Column(String, nullable=False)
    enum_options = Column(JSON, nullable=True)
    display_order = Column(Integer, nullable=False)


class ConversationSession(Base):
    __tablename__ = "conversation_sessions"

    session_id = Column(String, primary_key=True)
    state = Column(JSON, nullable=False)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    unit = Column(String, default="pcs")
    price = Column(Integer, nullable=True)
    attributes = Column(JSON, default=dict)


class ProductRelationship(Base):
    __tablename__ = "product_relationships"

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    relation_type = Column(String, nullable=False)
    quantity_formula = Column(String, nullable=True)
    condition_json = Column(JSON, default=dict)
