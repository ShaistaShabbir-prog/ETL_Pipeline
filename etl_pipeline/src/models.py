from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MyTable(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True) 
    date_of_birth = Column(String)  
    salary = Column(Float)  # Change String to Float for numeric salary

    def __repr__(self):
        return f"<MyTable(id={self.id}, name={self.name}, date_of_birth={self.date_of_birth}, salary={self.salary})>"
