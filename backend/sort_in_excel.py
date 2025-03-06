# import os
# import uuid
# import pandas as pd
# import requests
# from fastapi import FastAPI, UploadFile, File, HTTPException
# from fastapi.responses import FileResponse, HTMLResponse
# from fastapi.staticfiles import StaticFiles
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin
# from faster_whisper import WhisperModel
# from pydub import AudioSegment
# from tqdm import tqdm
# from pathlib import Path

# app = FastAPI()

# # Конфигурация
# AUDIO_TEMP_DIR = "temp_audio"
# KEYWORDS = ["в архиве", "архивный", "впервые", "не был", "не была", "не были", "давно",
#             "больше года", "архив", "первичная консультация",
#             "консультация", "не было", "первичное"]
# os.makedirs(AUDIO_TEMP_DIR, exist_ok=True)

# # Загрузка модели
# model = WhisperModel("large", device="cpu", compute_type="int8")

# # Mount static files
# app.mount("/static", StaticFiles(directory="static"), name="static")

# def check_keywords(text):
#     """Проверяет наличие ключевых слов в тексте"""
#     if not text:
#         return False
#     text_lower = text.lower()
#     return any(keyword in text_lower for keyword in KEYWORDS)

# async def process_audio(url):
#     """Обработка аудио с URL"""
#     try:
#         response = requests.get(url, timeout=10)
#         response.raise_for_status()
        
#         soup = BeautifulSoup(response.content, 'html.parser')
#         audio_links = [
#             urljoin(url, tag['src']) 
#             for tag in soup.find_all('source') 
#             if tag.get('src', '').lower().endswith(('.mp3', '.wav', '.ogg'))
#         ]
        
#         if not audio_links:
#             return {"status": "нет аудио"}
        
#         last_audio_url = audio_links[-1]
#         filename = os.path.join(AUDIO_TEMP_DIR, f"{uuid.uuid4()}.wav")
        
#         audio_content = requests.get(last_audio_url, timeout=10).content
#         with open(filename, 'wb') as f:
#             f.write(audio_content)
        
#         audio = AudioSegment.from_file(filename)
#         duration = audio.duration_seconds
        
#         audio = audio.set_frame_rate(16000).set_channels(1)
#         audio.export(filename, format="wav")
        
#         segments, _ = model.transcribe(filename, language="ru")
#         text = " ".join([segment.text for segment in segments])
        
#         status = "верно"
#         if duration > 50:
#             status = "требует проверки" if check_keywords(text) else "верно"
        
#         return {"status": status}
    
#     except Exception as e:
#         return {"status": f"ошибка: {str(e)}"}

# @app.post("/upload/")
# async def upload_file(file: UploadFile = File(...)):
#     """Эндпоинт для загрузки файла"""
#     if not file.filename.endswith(('.xlsx', '.xls')):
#         raise HTTPException(400, "Поддерживаются только Excel файлы")
    
#     temp_file = f"temp_{uuid.uuid4()}.xlsx"
#     with open(temp_file, "wb") as f:
#         f.write(await file.read())
    
#     try:
#         df = pd.read_excel(temp_file, header=2, names=["Запись разговора"])
#         results = []
        
#         for url in tqdm(df["Запись разговора"], desc="Обработка"):
#             results.append(await process_audio(url))
        
#         df["status"] = [res["status"] for res in results]
#         output_file = f"result_{uuid.uuid4()}.xlsx"
#         df.to_excel(output_file, index=False)
        
#         return FileResponse(
#             output_file,
#             filename="processed_result.xlsx",
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )
    
#     finally:
#         for f in [temp_file, output_file]:
#             if os.path.exists(f):
#                 os.remove(f)

# @app.get("/", response_class=HTMLResponse)
# async def main():
#     """Главная страница с формой загрузки"""
#     return """
#     <html>
#         <head>
#             <title>Анализатор записей</title>
#             <style>
#                 body { font-family: Arial, sans-serif; margin: 2rem; }
#                 .container { max-width: 600px; margin: 0 auto; }
#                 form { border: 1px solid #ccc; padding: 2rem; border-radius: 5px; }
#                 input[type="file"] { margin: 1rem 0; }
#                 button { background: #007bff; color: white; border: none; padding: 0.5rem 1rem; cursor: pointer; }
#             </style>
#         </head>
#         <body>
#             <div class="container">
#                 <h1>Загрузите Excel-файл для анализа</h1>
#                 <form action="/upload/" method="post" enctype="multipart/form-data">
#                     <input type="file" name="file" accept=".xlsx,.xls">
#                     <button type="submit">Анализировать</button>
#                 </form>
#             </div>
#         </body>
#     </html>
#     """

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)