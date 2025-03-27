# models.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MyTable(Base):
    __tablename__ = "my_table"

    id = Column(Integer, primary_key=True, index=True)
    column1 = Column(String, index=True)
    column2 = Column(String)

    def __repr__(self):
        return (
            f"<MyTable(id={self.id}, column1={self.column1}, column2={self.column2})>"
        )
