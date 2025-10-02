

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import gzip
import shutil
import os
import tempfile
from pathlib import Path

import tempfile

# Константы
WIND_DIRECTIONS = ['С', 'ССВ', 'СВ', 'ВСВ', 'В', 'ВЮВ', 'ЮВ', 'ЮЮВ', 'Ю', 'ЮЮЗ', 'ЮЗ', 'ЗЮЗ', 'З', 'ЗСЗ', 'СЗ', 'ССЗ']

WIND_NAME_MAPPING = {
    'Переменное направление': 'ХХ',
    'Штиль, безветрие': 'Х',
    'Ветер, дующий с севера': 'С',
    'Ветер, дующий с северо-северо-востока': 'ССВ',
    'Ветер, дующий с северо-востока': 'СВ',
    'Ветер, дующий с востоко-северо-востока': 'ВСВ',
    'Ветер, дующий с востока': 'В',
    'Ветер, дующий с востоко-юго-востока': 'ВЮВ',
    'Ветер, дующий с юго-востока': 'ЮВ',
    'Ветер, дующий с юго-юго-востока': 'ЮЮВ',
    'Ветер, дующий с юга': 'Ю',
    'Ветер, дующий с юго-юго-запада': 'ЮЮЗ',
    'Ветер, дующий с юго-запада': 'ЮЗ',
    'Ветер, дующий с западо-юго-запада': 'ЗЮЗ',
    'Ветер, дующий с запада': 'З',
    'Ветер, дующий с западо-северо-запада': 'ЗСЗ',
    'Ветер, дующий с северо-запада': 'СЗ',
    'Ветер, дующий с северо-северо-запада': 'ССЗ'
}

CUSTOM_COLORS = [
    "#4B0082",  # Темно-синий (индиго)
    "#0000FF",  # Ярко-синий
    "#4682B4",  # Стальной синий
    "#5F9EA0",  # Бирюзовый синий
    "#708090",  # Серый с синим оттенком
    "#A9A9A9",  # Тёмно-серый
    "#D3D3D3",  # Светло-серый
]

# Настройки визуализации
IMPORTANCE_DECAY_RATE = -0.22
TEMP_COLOR_MIN = -10
TEMP_COLOR_MAX = 30
DATE_TICKS_MAX = 10
POLAR_FIGURE_SIZE = (6, 6)
REGULAR_FIGURE_SIZE = (10, 6)

# Копирайт
COPYRIGHT_TEXT = '© 2025 Busheisha'


def validate_meteo_file(file_path: str) -> tuple[bool, str]:
    """
    Валидирует файл метеоданных на безопасность.
    
    Args:
        file_path: Путь к файлу .xls.gz
        
    Returns:
        tuple: (is_valid, message) - валидность и сообщение
    """
    
    # 1. Проверка расширения
    if not file_path.endswith('.xls.gz'):
        return False, "❌ Мы принимаем только файлы .xls.gz"
    
    # 2. Проверка что файл существует
    if not os.path.exists(file_path):
        return False, "❌ Файл не найден"
    
    # 3. Проверка что это gzip архив
    try:
        with gzip.open(file_path, 'rb') as f:
            f.read(1024)  # Читаем первые 1024 байта
    except gzip.BadGzipFile:
        return False, "❌ Файл повреждён или не является gzip архивом"
    except Exception as e:
        return False, f"❌ Ошибка при чтении архива: {str(e)}"
    
    # 4. Проверка что внутри Excel файл
    temp_dir = None
    try:
        # Создаём временный файл для распаковки
        temp_dir = tempfile.mkdtemp()
        temp_xls_path = os.path.join(temp_dir, 'temp.xls')
        
        # Распаковываем
        with gzip.open(file_path, 'rb') as f_in:
            with open(temp_xls_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Пытаемся прочитать как Excel
        df = pd.read_excel(temp_xls_path, nrows=1)
        
        return True, "✅ Файл прошёл валидацию"
        
    except Exception as e:
        return False, f"❌ Внутри архива должен быть Excel файл: {str(e)}"
    
    finally:
        # Очищаем временные файлы
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def extract_gzip_file(file_path: str) -> str:
    """Распаковывает .gz файл и возвращает путь к распакованному файлу."""
    output_path = file_path.replace(".xls.gz", ".xls")
    with gzip.open(file_path, 'rb') as file_in:
        with open(output_path, 'wb') as file_out:
            shutil.copyfileobj(file_in, file_out)
    return output_path


def clean_data(file_path: str) -> pd.DataFrame:
    """Очищает и подготавливает данные из Excel файла."""
    df = pd.read_excel(file_path)
    df.columns = df.iloc[5]
    df = df.drop(range(6))
    
    column_rename_map = {df.columns[0]: 'time'}
    df = df.rename(columns=column_rename_map)
    
    df['DD'] = df['DD'].replace(WIND_NAME_MAPPING)
    df = df.loc[~df['DD'].isin(['Х', 'ХХ'])]
    
    return df


def create_zero_filled_dataframe(winds: list[str], column_name: str = 'DD') -> pd.DataFrame:
    """Создает DataFrame с нулевыми значениями для всех направлений ветра."""
    return pd.Series(data=0, index=winds).to_frame(name=column_name)


def reindex_with_all_directions(data: pd.Series, winds: list[str]) -> pd.DataFrame:
    """Переиндексирует данные, чтобы включить все направления ветра."""
    zero_filled = create_zero_filled_dataframe(winds, data.name)
    
    result = pd.concat([data, zero_filled]).reset_index()
    result = result.drop_duplicates(subset=['index'])
    result = result.set_index('index')
    result = result.reindex(index=winds)
    result = result.reset_index()
    
    return result


def processing(df: pd.DataFrame, winds: list[str]) -> pd.DataFrame:
    """Обрабатывает данные для простой розы ветров."""
    wind_counts = df.groupby(['DD']).size().to_frame(name='DD')
    return reindex_with_all_directions(wind_counts['DD'], winds)


def smartrose_processing(df: pd.DataFrame, winds: list[str]) -> pd.DataFrame:
    """Обрабатывает данные для умной розы ветров с учетом временного веса."""
    rose = df.copy()
    rose['time'] = pd.to_datetime(rose['time'], dayfirst=True)
    
    reftime = rose.iloc[0, 0]
    rose['reftime'] = reftime
    rose['age'] = rose['reftime'] - rose['time']
    rose['age'] = (rose['age'].dt.components.hours + (rose['age'].dt.components.days * 24)) / 24
    rose['importance'] = np.exp(rose['age'] * IMPORTANCE_DECAY_RATE)
    rose['importance_wind'] = rose['Ff'] * rose['importance']
    
    windrose = rose.groupby('DD')['importance_wind'].sum()
    return reindex_with_all_directions(windrose, winds)


def _plot_polar_rose(data: pd.DataFrame, value_column: str, title: str, output_path: str) -> str:
    """Вспомогательная функция для создания полярного графика розы ветров."""
    angles = np.linspace(0, 360, len(WIND_DIRECTIONS), endpoint=False)
    theta = np.radians(angles)
    r = data[value_column].values
    
    # Закрываем линию
    theta_closed = np.concatenate([theta, [theta[0]]])
    r_closed = np.concatenate([r, [r[0]]])
    
    fig, ax = plt.subplots(figsize=POLAR_FIGURE_SIZE, subplot_kw=dict(projection='polar'))
    ax.plot(theta_closed, r_closed, linewidth=2)
    ax.fill(theta_closed, r_closed, alpha=0.25)
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_thetagrids(angles, WIND_DIRECTIONS)
    ax.set_yticklabels([])  # Убираем подписи радиальных значений
    ax.set_title(title, pad=20)
    
    _add_copyright(fig)
    
    plt.savefig(output_path, bbox_inches='tight', dpi=100)
    plt.close(fig)
    return output_path


def _add_copyright(fig):
    """Добавляет копирайт в правый нижний угол графика."""
    fig.text(0.995, 0.005, COPYRIGHT_TEXT, ha='right', va='bottom', fontsize=8, alpha=0.35)


def _setup_date_axis(ax):
    """Настраивает ось дат с автоматическим форматированием."""
    ax.xaxis.set_major_locator(plt.MaxNLocator(nbins=DATE_TICKS_MAX))
    plt.xticks(rotation=45, ha='right')


def create_windrose(file_path: str, first_image_path: str) -> str:
    """Создает простую розу ветров."""
    extracted_path = extract_gzip_file(file_path)
    try:
        df = clean_data(extracted_path)
        wind_data = processing(df, WIND_DIRECTIONS)
        return _plot_polar_rose(wind_data, 'DD', 'windrose', first_image_path)
    finally:
        if os.path.exists(extracted_path):
            os.remove(extracted_path)


def create_smartrose(file_path: str, second_image_path: str) -> str:
    """Создает умную розу ветров с учетом временного веса."""
    extracted_path = extract_gzip_file(file_path)
    try:
        df = clean_data(extracted_path)
        windrose_data = smartrose_processing(df, WIND_DIRECTIONS)
        return _plot_polar_rose(windrose_data, 'importance_wind', 'smartrose', second_image_path)
    finally:
        if os.path.exists(extracted_path):
            os.remove(extracted_path)


def create_combined_rose(file_path: str, output_image_path: str) -> str:
    """Создает совмещенный график с обычной и умной розой ветров."""
    extracted_path = extract_gzip_file(file_path)
    try:
        df = clean_data(extracted_path)
        
        # Получаем данные для обоих графиков
        simple_wind_data = processing(df, WIND_DIRECTIONS)
        smart_wind_data = smartrose_processing(df, WIND_DIRECTIONS)
        
        # Нормализуем данные для лучшего визуального сравнения
        simple_values = simple_wind_data['DD'].values
        smart_values = smart_wind_data['importance_wind'].values
        
        # Нормализуем на максимум, чтобы оба графика были в одном масштабе
        simple_max = simple_values.max()
        smart_max = smart_values.max()
        if simple_max > 0:
            simple_normalized = simple_values / simple_max
        else:
            simple_normalized = simple_values
            
        if smart_max > 0:
            smart_normalized = smart_values / smart_max
        else:
            smart_normalized = smart_values
        
        # Подготовка углов
        angles = np.linspace(0, 360, len(WIND_DIRECTIONS), endpoint=False)
        theta = np.radians(angles)
        
        # Закрываем линии
        theta_closed = np.concatenate([theta, [theta[0]]])
        simple_closed = np.concatenate([simple_normalized, [simple_normalized[0]]])
        smart_closed = np.concatenate([smart_normalized, [smart_normalized[0]]])
        
        # Создаем график
        fig, ax = plt.subplots(figsize=POLAR_FIGURE_SIZE, subplot_kw=dict(projection='polar'))
        
        # Рисуем smartrose (основной, менее прозрачный)
        ax.plot(theta_closed, smart_closed, linewidth=2.5, label='smartrose', color='#1f77b4')
        ax.fill(theta_closed, smart_closed, alpha=0.3, color='#1f77b4')
        
        # Рисуем windrose (наложение, более прозрачный - 1/3 от smartrose)
        ax.plot(theta_closed, simple_closed, linewidth=2, label='windrose', color='#1f77b4', linestyle='--')
        ax.fill(theta_closed, simple_closed, alpha=0.1, color='#1f77b4')
        
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_thetagrids(angles, WIND_DIRECTIONS)
        ax.set_yticklabels([])
        ax.set_title('роза ветров', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        
        _add_copyright(fig)
        
        plt.savefig(output_image_path, bbox_inches='tight', dpi=100)
        plt.close(fig)
        return output_image_path
    finally:
        if os.path.exists(extracted_path):
            os.remove(extracted_path)


def temperature_processing(df: pd.DataFrame) -> pd.DataFrame:
    """Обрабатывает данные температуры и влажности."""
    sorted_df = df.iloc[::-1].copy()
    sorted_df['U'] = pd.to_numeric(sorted_df['U'], errors='coerce')
    sorted_df['U'] = sorted_df['U'] - sorted_df['U'].min()
    sorted_df['U'] = sorted_df['U'].fillna(0).astype(int)
    sorted_df['T'] = pd.to_numeric(sorted_df['T'], errors='coerce')
    return sorted_df


def rain_processing(df: pd.DataFrame) -> pd.DataFrame:
    """Обрабатывает данные осадков."""
    df = df.iloc[::-1]
    rain_df = df[['time', 'W1', 'RRR', 'tR', 'sss']].copy()
    rain_df['RRR'] = pd.to_numeric(rain_df['RRR'], errors='coerce')
    rain_df['RRR'] = rain_df['RRR'].fillna(0)
    rain_df['sss'] = pd.to_numeric(rain_df['sss'], errors='coerce')
    rain_df['sss'] = rain_df['sss'].interpolate(method='linear')
    rain_df['tR'] = pd.to_numeric(rain_df['tR'], errors='coerce')
    rain_df['time'] = pd.to_datetime(rain_df['time'], errors='coerce', dayfirst=True).dt.date
    rain_df['W1'] = rain_df['W1'].fillna('').apply(lambda x: (x[:20] + '...') if len(x) > 20 else x)
    
    grouped_rain_df = rain_df.groupby('time').agg({
        'W1': lambda x: x.mode()[0] if not x.mode().empty else np.nan,
        'RRR': lambda x: (x.sum() / rain_df.loc[x.index, 'tR'].sum()) * 24 if rain_df.loc[x.index, 'tR'].sum() != 0 else np.nan,
        'sss': 'max'
    }).reset_index()
    
    return grouped_rain_df


def create_rain(file_path: str, fourth_image_path: str) -> str:
    """Создает график осадков."""
    extracted_path = extract_gzip_file(file_path)
    try:
        df = clean_data(extracted_path)
        rain_df = rain_processing(df)
        
        fig, ax = plt.subplots(figsize=REGULAR_FIGURE_SIZE)
        
        # Получаем уникальные типы осадков и создаем маппинг цветов
        unique_w1 = rain_df['W1'].unique()
        color_map = {w1: CUSTOM_COLORS[i % len(CUSTOM_COLORS)] for i, w1 in enumerate(unique_w1)}
        
        # Группируем данные по типу осадков для создания легенды
        for w1_type in unique_w1:
            mask = rain_df['W1'] == w1_type
            ax.bar(rain_df[mask]['time'], rain_df[mask]['RRR'],
                   label=w1_type, color=color_map[w1_type])
        
        ax.set_xlabel('время')
        ax.set_ylabel('количество осадков, мм')
        ax.set_title('осадки')
        
        # Вторая ось Y для снежного покрова
        ax2 = ax.twinx()
        ax2.plot(rain_df['time'], rain_df['sss'], color='black', linewidth=2,
                 label='высота снежного покрова, см')
        ax2.set_ylabel('высота снежного покрова, см')
        
        # Настройка легенды
        ax.legend(title='тип осадков', bbox_to_anchor=(1.22, 1), loc='upper left')
        
        _setup_date_axis(ax)
        
        _add_copyright(fig)
        
        plt.savefig(fourth_image_path, bbox_inches='tight', dpi=100)
        plt.close(fig)
        return fourth_image_path
    finally:
        if os.path.exists(extracted_path):
            os.remove(extracted_path)


def create_temperature(file_path: str, third_image_path: str) -> str:
    """Создает график температуры и влажности."""
    extracted_path = extract_gzip_file(file_path)
    try:
        df = clean_data(extracted_path)
        sorted_df = temperature_processing(df)
        
        # Делаем график шире на 20% для лучшей читаемости с colorbar
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Scatter plot с размером и цветом
        scatter = ax.scatter(sorted_df['time'], sorted_df['T'],
                            s=sorted_df['U'] * 10,
                            c=sorted_df['T'],
                            cmap='RdBu_r',
                            vmin=TEMP_COLOR_MIN, vmax=TEMP_COLOR_MAX,
                            edgecolors='black', linewidths=0.5,
                            alpha=0.7)
        
        ax.set_xlabel('время')
        ax.set_ylabel('температура, °C')
        ax.set_title('температура и влажность')
        
        # Добавляем цветовую шкалу
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('температура, °C')
        
        _setup_date_axis(ax)
        
        _add_copyright(fig)
        
        plt.savefig(third_image_path, bbox_inches='tight', dpi=100)
        plt.close(fig)
        return third_image_path
    finally:
        if os.path.exists(extracted_path):
            os.remove(extracted_path)

def validate_meteo_file(file_path: str) -> tuple[bool, str]:
    """
    Валидирует файл метеоданных на безопасность.
    
    Args:
        file_path: Путь к файлу .xls.gz
        
    Returns:
        tuple: (is_valid, message) - валидность и сообщение
    """
    
    # 1. Проверка расширения
    if not file_path.endswith('.xls.gz'):
        return False, "❌ Мы принимаем только файлы .xls.gz"
    
    # 2. Проверка что файл существует
    if not os.path.exists(file_path):
        return False, "❌ Файл не найден"
    
    # 3. Проверка что это gzip архив
    try:
        with gzip.open(file_path, 'rb') as f:
            f.read(1024)  # Читаем первые 1024 байта
    except gzip.BadGzipFile:
        return False, "❌ Файл повреждён или не является gzip архивом"
    except Exception as e:
        return False, f"❌ Ошибка при чтении архива: {str(e)}"
    
    # 4. Проверка что внутри Excel файл
    temp_dir = None
    try:
        # Создаём временный файл для распаковки
        temp_dir = tempfile.mkdtemp()
        temp_xls_path = os.path.join(temp_dir, 'temp.xls')
        
        # Распаковываем
        with gzip.open(file_path, 'rb') as f_in:
            with open(temp_xls_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Пытаемся прочитать как Excel
        df = pd.read_excel(temp_xls_path, nrows=1)
        
        return True, "✅ Файл прошёл валидацию"
        
    except Exception as e:
        return False, f"❌ Внутри архива должен быть Excel файл: {str(e)}"
    
    finally:
        # Очищаем временные файлы
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
