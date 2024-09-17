from sqlalchemy import JSON, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email_address = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)

    models = relationship("Model", back_populates="user")


class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    algorithm = Column(String, nullable=False)
    inputs = Column(JSON, nullable=False, default=list)
    weights = Column(JSON, nullable=False, default=list)

    user = relationship("User", back_populates="models")
