from fastapi import APIRouter, File, UploadFile
from src.repositories.uploadFile import get_text_format


router = APIRouter(prefix="/uploadfile", tags=["uploadfile"])



@router.post("",
            responses={400: {"description": "Bad request"}} )
def transcrib_sound_file(file: UploadFile = File(...)):
    try:
        return {"filename": get_text_format(file.file), "status": "success"}
    except Exception as e:
        return {"error": str(e)}
