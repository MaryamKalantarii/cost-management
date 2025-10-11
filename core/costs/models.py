from sqlalchemy import Column, Integer, String,Float ,ForeignKey
from core.core.database import Base
from sqlalchemy.orm import relationship

class Cost(Base):
    __tablename__ = "costs"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("UserModel", back_populates="costs")