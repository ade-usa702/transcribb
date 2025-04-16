import io
import requests
from bs4 import BeautifulSoup
from faster_whisper import WhisperModel
from pydub import AudioSegment



# Конфигурация
KEYWORDS = ["в архиве", "архивный", "впервые", "не был", "не была", "не были", "давно",
            "больше года", "архив", "первичная консультация",
            "консультация", "не было", "первичное"]

KEYWORDS_BRAK = ["перенести", "записана","записана сегодня","была сегодня","была вчера","неделю назад",
                 "месяц назад","отменить","справку","справка","на прошлой неделе","у меня запись на прием",
                 "я обслуживаюсь","там были сегодня","там была сегодня","перенести прием","опаздываю",
                 "заболел","заболела","не смогу придти","перенесите запись","не приду"]


# Загрузка модели
model = WhisperModel("large", device="cpu", compute_type="int8") #cuda float16


def check_keywords(text):
    """Проверяет наличие ключевых слов в тексте"""
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in KEYWORDS)

def w_keywords(text: str) -> list[str]:  
    return [keyword for keyword in KEYWORDS_BRAK if keyword in text.lower()]


def process_audio(url):
    """Обработка аудио с URL"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Поиск аудио-ссылок
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            audio_links = []
            count_link = 0
            for source in soup.find_all('source', src=True):
                if source['src']:
                    audio_links.append(source['src'])
                    count_link += 1
        
        if not audio_links:
            return "нет аудио"
        
        # Скачивание аудио в память
        audio_response = requests.get(audio_links[-1], timeout=20)
        audio_response.raise_for_status()
        
        # Обработка аудио в памяти
        with io.BytesIO(audio_response.content) as audio_buffer:
            # Конвертация в формат WAV
            audio = AudioSegment.from_file(audio_buffer)
            audio = audio.set_frame_rate(16000).set_channels(1)
            
            # Конвертация в сырые данные для Whisper
            with io.BytesIO() as wav_buffer:
                audio.export(wav_buffer, format="wav")
                wav_buffer.seek(0)
                
                # Транскрибация
                segments, _ = model.transcribe(wav_buffer, language="ru")
                text = " ".join(segment.text for segment in segments)
        
        # Определение статуса
        duration = len(audio) / 1000  # Продолжительность в секундах
        if duration < 50:
             status = "длительность менее 50 секунд"
        elif duration > 50 and check_keywords(text):
            status = "требует проверки"
        else:
            status = "верно"

        details = f" ({w_keywords(text)})" if status == "верно" else ""
        return f"{status}; {count_link} аудиодорожки; {details}"
        
    except Exception as e:
        return f"ошибка: {str(e)}"