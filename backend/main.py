from typing import Union
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import pandas as pd
import uuid
import os
from tqdm import tqdm
import sort_in_excel
# from decodeFile import getTextFormat
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.get("/add")
# def read_root():
#     return {"Hello": "World"}


@app.post("/uploadfile/")
def transcrib_sound_file(file: UploadFile = File(...)):
    try:

        mockData = '[0:00:00.000 --> 0:00:02.080] Стоматология, все свои, здравствуйте. [0:00:04.280 --> 0:00:07.640] Здравствуйте, а соедините меня с Войковской. [0:00:08.439 --> 0:00:10.300] Когда вы были в нашей клинике в последний раз? [0:00:10.560 --> 0:00:11.339] Две недели назад. [0:00:12.300 --> 0:00:15.339] Составайтесь на линии, пожалуйста, вас соединю с клиникой напрямую.'

        # return {"filename": getTextFormat(file.file), "status": "success"}
        return {"filename": mockData, "status": "success"}
    except Exception as e:
        return {"error": str(e)}
    

@app.post("/othercalls/")
async def  analyze_excel_file(file: UploadFile = File(..., pattern=r".*\.xlsx$")): 
    temp_file = f"temp_{uuid.uuid4()}.xlsx"
    with open(temp_file, "wb") as f:
        f.write(await file.read())
    
    try:
        df = pd.read_excel(temp_file, header=2, names=["Запись разговора"])
        results = []
        
        for url in tqdm(df["Запись разговора"], desc="Обработка"):
            results.append(await sort_in_excel.process_audio(url))
        
        df["status"] = [res["status"] for res in results]
        output_file = f"result_{uuid.uuid4()}.xlsx"
        df.to_excel(output_file, index=False)
        
        return FileResponse(
            output_file,
            filename="processed_result.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    finally:
        for f in [temp_file, output_file]:
            if os.path.exists(f):
                os.remove(f)
