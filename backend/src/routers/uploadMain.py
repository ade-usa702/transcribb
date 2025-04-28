from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import FileResponse
from werkzeug.http import parse_options_header
from openpyxl import load_workbook
from repositories.uploadMain import RequestRepository, RequestFilter
import re
import os

from sqlalchemy.orm import Session
from database import get_db

router = APIRouter(prefix ='/mainjob', tags=['mainjob'])




@router.get("",
             responses={400: {"descripton": "Bad request"}} )
def get_filter(db: Session = Depends(get_db)):
    return RequestRepository.get_filtered_requests(db)


@router.post("/search",
             responses={400: {"descripton": "Bad request"}} )
def find_for_column(filters: RequestFilter, db: Session = Depends(get_db)):
    try:
        return RequestRepository(db).apply_filters(filters)
    except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Ошибка скачивания файла: {str(e)}'
            )    



@router.post("",
             responses={400: {"descripton": "Bad request"}} )
def download_file(output_file, db):
    try:
        if output_file:
            safe_file = re.sub(r'[\\/:*?"<>|]', '_', output_file)
            safe_file = safe_file[:50].strip()

        else:
            safe_file = "main_result"

        if not safe_file.endswith(".xlsx"):
            safe_file += ".xlsx"

        output_path = os.path.join(safe_file)
        db.to_excel(output_path, index=False)

        return FileResponse(
            output_path,
            filename=safe_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Ошибка скачивания файла: {str(e)}'
        )    
