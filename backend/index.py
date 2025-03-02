import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from faster_whisper import WhisperModel
from pydub import AudioSegment
from tqdm import tqdm

# Конфигурация

EXCEL_FILE = input(filetypes=[("Excel files", "*.xlsx;*.xls"), ("All files", "*.*")])
OUTPUT_FILE  = input(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
AUDIO_TEMP_DIR = "temp_audio"
KEYWORDS = ["в архиве", "архивный",  "впервые", "не был", "не была", "не были", "давно",
             "больше года", "архив", "первичная консультация",
               "консультация", "не было", "первичное"]
os.makedirs(AUDIO_TEMP_DIR, exist_ok=True)

# Загрузка модели
model = WhisperModel("small", device="cpu", compute_type="int8")  # Используйте 'small' для баланса скорости/точности

def check_keywords(text):
    """Проверяет наличие ключевых слов в тексте (без учета регистра)"""
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in KEYWORDS)

def process_audio(url):
    """Обрабатывает URL и возвращает статус"""
    try:
        # 1. Загрузка страницы
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # 2. Поиск аудиофайлов
        soup = BeautifulSoup(response.content, 'html.parser')
        audio_links = [
            urljoin(url, tag['href']) 
            for tag in soup.find_all('source src', href=True) 
            if tag['href'].lower().endswith(('.mp3', '.wav', '.ogg'))
        ]
        
        if not audio_links:
            return { "status": "нет аудио"}
        
        # 3. Скачивание последнего аудио
        last_audio_url = audio_links[-1]
        filename = os.path.join(AUDIO_TEMP_DIR, os.path.basename(last_audio_url))
        
        with open(filename, 'wb') as f:
            f.write(requests.get(last_audio_url, timeout=10).content)
        
        # 4. Конвертация и получение длительности
        audio = AudioSegment.from_file(filename)
        duration = audio.duration_seconds  # Получаем длительность
        
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(filename, format="wav")
        
        # 5. Транскрибация
        result = model.transcribe(filename, language="ru", fp16=False)
        text = result["text"]
        
        # 6. Проверка условий
        status = "верно"
        if duration > 50:
            status = "требует проверки" if check_keywords(text) else "верно"
        
        return {"status": status}
    
    except Exception as e:
        print(f"Ошибка: {url} — {str(e)}")
        return { "status": "ошибка"}

def main():
    df = pd.read_excel(EXCEL_FILE, header=2, names=["Запись разговора"])
    results = []
    
    for url in tqdm(df["Запись разговора"], desc="Обработка"):
        results.append(process_audio(url))
    
    # Добавляем результаты в DataFrame
    df["status"] = [res["status"] for res in results]
    
    # Сохраняем
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"Готово! Результаты в {OUTPUT_FILE}")

if __name__ == "__main__":
    main()