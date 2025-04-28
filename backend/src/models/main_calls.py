from sqlalchemy import Column, Integer, String, DateTime
from database import Base



class CallModel(Base):
    __tablename__ = "requests"

    request_id = Column(Integer, primary_key=True, index=False)
    type_request = Column(String, nullable=False)
    date = Column(DateTime)
    phone = Column(String, nullable=False)
    comment_req = Column(String, nullable=False)
    service = Column(String, nullable=False)
    sources = Column(String, nullable=False)
    fio = Column(String, nullable=False)
    links = Column(String, nullable=False)


