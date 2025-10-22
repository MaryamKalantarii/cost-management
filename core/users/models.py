from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from passlib.context import CryptContext
from core.database import Base
from sqlalchemy.orm import relationship

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(250), nullable=False, unique=True)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime, server_default=func.now())
    updated_date = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
    costs= relationship("Cost", back_populates="user")
    
    
    def hash_password(self, plain_password: str) -> str:
        """Hashes the given password using bcrypt."""
        return pwd_context.hash(plain_password)
    
    
    def verify_password(self, plain_password: str) -> bool:
        """Verifies the given password against the stored hash."""
        return pwd_context.verify(plain_password, self.password)
    
    def set_password(self, plain_text: str) -> None:
        self.password = self.hash_password(plain_text)