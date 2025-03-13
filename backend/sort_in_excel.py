import os
import uuid
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from faster_whisper import WhisperModel
from pydub import AudioSegment



# Конфигурация
AUDIO_TEMP_DIR = "temp_audio"
KEYWORDS = ["в архиве", "архивный", "впервые", "не был", "не была", "не были", "давно",
            "больше года", "архив", "первичная консультация",
            "консультация", "не было", "первичное"]
os.makedirs(AUDIO_TEMP_DIR, exist_ok=True)

# Загрузка модели
model = WhisperModel("large", device="cpu", compute_type="int8")


def check_keywords(text):
    """Проверяет наличие ключевых слов в тексте"""
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in KEYWORDS)

async def process_audio(url):
    """Обработка аудио с URL"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        audio_links = [
            urljoin(url, tag['src']) 
            for tag in soup.find_all('source') 
            if tag.get('src', '').lower().endswith(('.mp3', '.wav', '.ogg'))
        ]
        
        if not audio_links:
            return {"status": "нет аудио"}
        
        last_audio_url = audio_links[-1]
        filename = os.path.join(AUDIO_TEMP_DIR, f"{uuid.uuid4()}.wav")
        
        audio_content = requests.get(last_audio_url, timeout=10).content
        with open(filename, 'wb') as f:
            f.write(audio_content)
        
        audio = AudioSegment.from_file(filename)
        duration = audio.duration_seconds
        
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(filename, format="wav")
        
        segments, _ = model.transcribe(filename, language="ru")
        text = " ".join([segment.text for segment in segments])
        
        status = "верно"
        if duration > 50:
            status = "требует проверки" if check_keywords(text) else "верно"
        
        return {"status": status}
    
    except Exception as e:
        return {"status": f"ошибка: {str(e)}"}
