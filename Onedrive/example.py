import pandas as pd
from sqlalchemy import create_engine, types
from sqlalchemy.dialects.postgresql import BIGINT, TIMESTAMP

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/maincalls"
engine = create_engine(DATABASE_URL)

def load_and_process_excel(file_list):
    selected_columns = [
        '№ \nзаявки',
        'Дата \nзаявки',
        'ANumber',
        'comment_req',
        'Услуга',
        'Источник (Авто)',
        'Записан',
        'Запись\n звонка',
        'Тип \nисточника'
    ]
    
    # Инициализация общего DataFrame перед циклом
    combined_df = pd.DataFrame()

    for file_path in file_list:
        # Чтение файла
        sheets = pd.read_excel(
            file_path,
            sheet_name=None,
            usecols=lambda col: col in selected_columns  # Безопасная фильтрация колонок
        )
        
        # Фильтрация листов
        sheets = {
            name: df 
            for name, df in sheets.items() 
            if name not in ['Звонки', 'Согл', 'Стом']
        }

        # Объединение листов одного файла
        file_df = pd.concat(sheets.values(), ignore_index=True)
        
        # Добавление в общий DataFrame
        combined_df = pd.concat([combined_df, file_df], ignore_index=True)

    # Единоразовая обработка после сбора всех данных
    combined_df = combined_df[selected_columns].dropna(how='all')
    
    # Переименование колонок
    column_mapping = {
        '№ \nзаявки': 'request_id',
        'Дата \nзаявки': 'date',
        'ANumber': 'phone',
        'comment_req': 'comment_req',
        'Услуга': 'service',
        'Источник (Авто)': 'sources',
        'Записан': 'fio',
        'Запись\n звонка': 'links',
        'Тип \nисточника': 'type_request'
    }
    combined_df = combined_df.rename(columns=column_mapping)

    # Функция предобработки
    def preprocess_data(df):
        # Конвертация даты
        df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
        
        # Номер заявки
        df['request_id'] = pd.to_numeric(df['request_id'], errors='coerce')
        
        # Телефон
        df['phone'] = (
            df['phone']
            .astype(str)
            .str.replace(r'[^0-9+]', '', regex=True)
            .str.slice(0, 14)
        )

        # Обработка текстовых полей
        text_rules = {
            'type_request': 10,
            'service': 30,
            'sources': 30,
            'fio': 80,
            'comment_req': 200
        }
        
        for col, max_len in text_rules.items():
            df[col] = df[col].astype(str).str.strip().str[:max_len]        
        return df.dropna(how='all')

    return preprocess_data(combined_df)

# Запуск обработки
try:
    file_list = [
        '2024_03-МЕД.xlsx',
        '2024_04-МЕД.xlsx',
        '2024_04-МЕД.xlsx',
        '2024_05-МЕД.xlsx',
        '2024_03-МЕД.xlsx',
        '2024_06-МЕД.xlsx',
        '2024_07-МЕД.xlsx',
        '2024_08-МЕД.xlsx',
        '2024_09-МЕД.xlsx',
        '2024_10-МЕД.xlsx',
        '2024_11-МЕД.xlsx',
        '2024_12-МЕД.xlsx',
        '2025_01-МЕД.xlsx',
        '2025_02-МЕД.xlsx',
        '2025_03-МЕД.xlsx'
    ]
    
    processed_df = load_and_process_excel(file_list)
    
    # Загрузка в БД
    dtype = {
        'date': TIMESTAMP(timezone=False),
        'links': types.VARCHAR(500),
        'phone': types.VARCHAR(14),
        'service': types.VARCHAR(30)
    }
    

    processed_df.to_sql(
        name='maincall',
        con=engine,
        if_exists='append',
        index=False,
        dtype=dtype,
        method='multi'
    )
    
    print(f"Успешно загружено {len(processed_df)} записей!")

except Exception as e:
    print(f"Ошибка: {str(e)}")
    if 'processed_df' in locals():
        print("Пример строки:", processed_df.iloc[0].to_dict())
   
