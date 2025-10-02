import os
import gzip
import tempfile
import shutil
import pandas as pd


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
