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
def create_upload_file(file: UploadFile = File(...)):
    try:
        # Сохраняем файл
        # dest = UPLOAD_DIR / file.filename
        # with dest.open("wb") as buffer:
        #     shutil.copyfileobj(file.file, buffer)

        mockData = '[0:00:00.000 --> 0:00:02.080] Стоматология, все свои, здравствуйте. [0:00:04.280 --> 0:00:07.640] Здравствуйте, а соедините меня с Войковской. [0:00:08.439 --> 0:00:10.300] Когда вы были в нашей клинике в последний раз? [0:00:10.560 --> 0:00:11.339] Две недели назад. [0:00:12.300 --> 0:00:15.339] Составайтесь на линии, пожалуйста, вас соединю с клиникой напрямую.'

        # return {"filename": getTextFormat(file.file), "status": "success"}
        return {"filename": mockData, "status": "success"}
    except Exception as e:
        return {"error": str(e)}
    

    