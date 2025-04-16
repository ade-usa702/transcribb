import pandas as pd
from sqlalchemy import create_engine, types
from sqlalchemy.dialects.postgresql import BIGINT, TIMESTAMP

# Настройки подключения
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/seconddb"
engine = create_engine(DATABASE_URL)

def load_and_process_excel(file_path):

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
    # Чтение Excel-файла с обработкой пустых колонок
    sheets = pd.read_excel(
        file_path,
        sheet_name=["3", "4"],
        usecols=selected_columns  # Игнорируем технические колонки
    )

    # Объединение данных из всех листов
    combined_df = pd.concat(sheets.values(), ignore_index=True)
    combined_df = combined_df[selected_columns]
    combined_df = combined_df.dropna(how='all')  # Удаление полностью пустых строк

    # Переименование колонок для SQL
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

    # Преобразование данных
    def preprocess_data(df):
        # Обработка даты с разными форматами

        df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
        
        # Номер заявки
        df['request_id'] = pd.to_numeric(
            df['request_id'],
            errors='coerce'
        )
        
        # Телефон
        df['phone'] = (
            df['phone']
            .astype(str)
            .str.replace(r'[^0-9+]', '', regex=True)
            .str.slice(0, 20)
        )
        
        # Текстовые поля
        text_fields = {
            'type_request': 20,
            'comment_req': 200,
            'service': 20,
            'sources': 20,
            'fio': 100, 
            'links': 500
        }
        
        for col, max_len in text_fields.items():
            df[col] = df[col].astype(str).str.slice(0, max_len)
        
        
        # Удаление полностью пустых строк
        return df.dropna(how='all')

    return preprocess_data(combined_df)

processed_df = None
try:
    processed_df = load_and_process_excel('2024_08-МЕД.xlsx')
    print("Столбцы для загрузки:", processed_df.columns.tolist())
    
    # Типы данных для SQLAlchemy
    dtype = {
        'date': TIMESTAMP(timezone=False),
        'links': types.VARCHAR(20),
        'phone': types.VARCHAR(20),
        'service': types.VARCHAR(20)
    }
    
    # Загрузка в БД
    processed_df.to_sql(
        name='requests',
        con=engine,
        if_exists='append',
        index=False,
        dtype=dtype,
        method='multi'
    )
    print(f"\nУспешно загружено {len(processed_df)} записей!")

except Exception as e:
    print(f"\nКритическая ошибка: {str(e)}")
    if processed_df is not None:
        print("Пример проблемной строки:")
        print(processed_df.iloc[0].to_dict())