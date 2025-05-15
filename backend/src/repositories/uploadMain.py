# src/repositories/request.py
from datetime import datetime, time, date
from sqlalchemy import func, or_
import re
from typing import Optional, Dict
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models.main_calls import CallModel


def normalize_phone(phone: str) -> str:
    """Приводит телефон к формату 79118281562"""
    # Удаляем все нецифровые символы
    digits = re.sub(r'\D', '', phone)
    
    # Обработка разных форматов
    if len(digits) == 11:
        if digits.startswith('8'):
            return '7' + digits[1:]
        return digits
    elif len(digits) == 10:
        return '7' + digits
    elif len(digits) < 10:
        # Для коротких номеров добавим базовый код (настройте под ваши нужды)
        return '7911' + digits[-7:]  # Пример для номеров типа 18281562
    return digits  # Возвращаем как есть, если формат неизвестен

# Pydantic модель для валидации параметров
class RequestFilter(BaseModel):
    phone: Optional[str] = None
    fio: Optional[str] = None
    request_id: Optional[int] = None
    sources: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    def get(self, key:str) -> bool:
        return getattr(self, key) is not None

class RequestRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def apply_filters(self, filters: RequestFilter):

        
        query = self.db_session.query(CallModel)
        if filters.get('phone'):
            normalized_phone = normalize_phone(filters.phone)
            query = query.filter(CallModel.phone == normalized_phone)
            
        if filters.get('fio'):
            query = query.filter(CallModel.fio == filters.fio)
        if filters.get('request_id'):
            query = query.filter(CallModel.request_id == filters.request_id)

        if filters.get('sources'):
            source = filters.sources.lower().strip()
            
            # Москва
            if source in {"мск", "москва"}:
                query = query.filter(
                    or_(
                        CallModel.sources.ilike("%мск%"),
                        CallModel.sources.ilike("%москва%")
                    )
                )
            
            # Самара
            elif source == "самара":
                query = query.filter(
                    CallModel.sources.ilike("%самара%")
                )
            
            # Волгоград
            elif source in {"волгоград", "влгд"}:
                query = query.filter(
                    or_(
                        CallModel.sources.ilike("%влгд%"),
                        CallModel.sources.ilike("%волгоград%")
                    )
                )
            
            # Санкт-Петербург
            elif source in {"питер", "спб"}:
                query = query.filter(
                    or_(
                        CallModel.sources.ilike("%питер%"),
                        CallModel.sources.ilike("%спб%")
                    )
                )
            
            # Нижний Новгород
            elif source in {"нн", "нижний", "новгород"}:
                query = query.filter(
                    or_(
                        CallModel.sources.ilike("%нн%"),
                        CallModel.sources.ilike("%нижний%"),
                        CallModel.sources.ilike("%новгород%")
                    )
                )
            
            # Екатеринбург
            elif source in {"екб", "екат", "екатеринбург"}:
                query = query.filter(
                    or_(
                        CallModel.sources.ilike("%екб%"),
                        CallModel.sources.ilike("%екат%"),  # Добавлено
                        CallModel.sources.ilike("%екатеринбург%")
                    )
                )
            else:
                # Если источник не распознан, ищем точное совпадение
                query = query.filter(CallModel.sources.ilike(f"%{source}%"))

                print(query.all())
        if filters.get('start_date') or filters.get('end_date'):
            print(filters.start_date, filters.end_date)
            if filters.start_date:
                query = query.filter(CallModel.data >= filters.start_date)
            
            if filters.end_date:
                query = query.filter(CallModel.data <= filters.end_date)


        return query.all()
    
    

    def get_filtered_requests(self, filter_params: Dict):
        # Валидация и нормализация параметров
        validated_params = RequestFilter(**filter_params)
        return self.apply_filters(validated_params)
    