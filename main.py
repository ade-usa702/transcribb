from typing import Union
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
# from decodeFile import getTextFormat
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/add")
def read_root():
    return {"Hello": "World"}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    try:
        # Сохраняем файл
        # dest = UPLOAD_DIR / file.filename
        # with dest.open("wb") as buffer:
        #     shutil.copyfileobj(file.file, buffer)
        # getTextFormat(file)
        return {"filename": file.filename, "status": "success"}
    except Exception as e:
        return {"error": str(e)}