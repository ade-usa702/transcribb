from sqlalchemy import Column, Integer, String, DateTime, Date, Time
from database import Base



class CallModel(Base):
    __tablename__ = "maincall"

    request_id = Column(Integer, primary_key=True, index=False)
    type_request = Column(String, nullable=False)
    data = Column(Date)
    time = Column(Time)
    phone = Column(String, nullable=False)
    comment_req = Column(String, nullable=False)
    service = Column(String, nullable=False)
    sources = Column(String, nullable=False)
    fio = Column(String, nullable=False)
    links = Column(String, nullable=False)


