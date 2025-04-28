# src/repositories/request.py
from datetime import datetime, time
from typing import Optional, Dict
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models.main_calls import CallModel

# Pydantic модель для валидации параметров
class RequestFilter(BaseModel):
    phone: Optional[str] = None
    fio: Optional[str] = None
    request_id: Optional[int] = None
    sources: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    def get(self, key:str) -> bool:
        return getattr(self, key) is not None

class RequestRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def apply_filters(self, filters: RequestFilter):
        query = self.db_session.query(CallModel)

        if filters.get('phone'):
            query = query.filter(CallModel.phone == filters.phone)
        if filters.get('fio'):
            query = query.filter(CallModel.fio == filters.fio)
        if filters.get('request_id'):
            query = query.filter(CallModel.request_id == filters.request_id)
        if filters.get('sources'):
            query = query.filter(CallModel.sources == filters.sources)

        if filters.get('start_date') or filters.get('end_date'):
            # Приводим даты к началу и концу дня соответственно

            if filters.get('start_date'):
                # Начало дня (00:00:00)
                start_date = datetime.combine(filters.start_date, time.min)
                query = query.filter(CallModel.date >= start_date)
            
            if filters.get('end_date'):
                # Конец дня (23:59:59.999999)
                end_date = datetime.combine(filters.end_date.date(), time.max)
                query = query.filter(CallModel.date <= end_date)



        return query.all()
    
    

    def get_filtered_requests(self, filter_params: Dict):
        # Валидация и нормализация параметров
        validated_params = RequestFilter(**filter_params)
        return self.apply_filters(validated_params)
    