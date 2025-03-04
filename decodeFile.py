from faster_whisper import WhisperModel
from tqdm import tqdm
import datetime

# Укажите путь к вашей модели
model = WhisperModel("large", device="cpu", compute_type="int8")

def format_time(seconds: float) -> str:
    """Форматирует время из секунд в формат HH:MM:SS.ms"""
    return str(datetime.timedelta(seconds=seconds)).split(".")[0] + f".{int(seconds % 1 * 1000):03d}"

def transcribe_audio(file_path):
    """Транскрибирует аудиофайл и возвращает текст с временными метками"""
    segments, info = model.transcribe(file_path, language="ru")
    
    full_text = ""
    for segment in tqdm(segments, desc="Обработка аудио"):
        # Форматируем временные метки
        start_time = format_time(segment.start)
        end_time = format_time(segment.end)
        
        # Форматируем строку с временными метками
        timestamped_text = f"[{start_time} --> {end_time}] {segment.text}"
        print(timestamped_text)
        
        full_text += timestamped_text + "\n"
    
    return full_text.strip()

def getTextFormat(audio_file_path):

    result = transcribe_audio(audio_file_path)

    return result

# Сохранение результата в файл
# with open("transcription2.txt", "w", encoding="utf-8") as f:
#     f.write(result)