import logging
import os
import datetime
import config

if config.ENABLE_LOGGING:
  logger = logging.getLogger(__name__)
else:
  logger = logging.getLogger(__name__)
  logger.setLevel(logging.CRITICAL)

def _get_history_file_path(purchase_type: str) -> str:
  # Вспомогательная функция для определения пути к файлу истории QR-кодов.
  # Путь зависит от типа магазина (ПравдаКофе или ХС).
  base_dir = os.path.dirname(os.path.abspath(__file__))
  if purchase_type == "pravdakofe":
      return os.path.join(base_dir, '..', config.QR_HISTORY_FILE_PRAVDAKOFE)
  elif purchase_type == "hs":
      return os.path.join(base_dir, '..', config.QR_HISTORY_FILE_HS)
  else:
      # Если передан неизвестный тип покупки, выбрасываем ошибку.
      raise ValueError(f"Неизвестный тип покупки: {purchase_type}")

def record_qr(user_id: int, qr_data: str, purchase_type: str, phone_number: str = None):
  # Записывает данные использованного QR-кода в соответствующий файл истории.
  # Номер телефона записывается только для ХС (так как это ведет к лояльности ПравдаКофе).
  try:
      history_file_path = _get_history_file_path(purchase_type)
      timestamp = datetime.datetime.now().isoformat() # Получаем текущее время для записи.

      with open(history_file_path, 'a') as f: # Открываем файл в режиме добавления ('a').
          if purchase_type == "hs" and phone_number: # Теперь для ХС
              f.write(f"{timestamp},{user_id},{qr_data},{phone_number}\n")
              logger.info(f"QR-код '{qr_data}' от пользователя {user_id} (телефон: {phone_number}) записан в историю ХС.")
          else:
              # Для ПравдаКофе только QR-код и ID пользователя.
              f.write(f"{timestamp},{user_id},{qr_data}\n")
              logger.info(f"QR-код '{qr_data}' от пользователя {user_id} записан в историю ПравдаКофе.")
  except IOError as e:
      logger.error(f"Ошибка записи QR-кода в файл истории {history_file_path}: {e}")
  except ValueError as e:
      logger.error(f"Ошибка получения пути к файлу истории: {e}")

def is_qr_duplicate(qr_data: str, purchase_type: str) -> bool:
  # Проверяет, был ли данный QR-код уже использован ранее.
  # Логика проверки зависит от настроек в config.py для каждого типа магазина.
  logger.info(f"Вызов is_qr_duplicate для типа покупки: '{purchase_type}', QR-данные: '{qr_data}'")

  # Проверяем, включена ли проверка на дубликаты для данного типа покупки.
  # Логика проверки дубликатов теперь: ПравдаКофе запрещает дубликаты, ХС - разрешает.
  if purchase_type == "pravdakofe":
      logger.info(f"Конфигурация CHECK_DUPLICATE_QR_PRAVDAKOFE: {config.CHECK_DUPLICATE_QR_PRAVDAKOFE}")
      if not config.CHECK_DUPLICATE_QR_PRAVDAKOFE: # Если False, то дубликаты разрешены
          logger.info("Проверка на дубликаты QR-кодов отключена для ПравдаКофе. Возвращаем False.")
          return False
  elif purchase_type == "hs":
      logger.info(f"Конфигурация CHECK_DUPLICATE_QR_HS: {config.CHECK_DUPLICATE_QR_HS}")
      if not config.CHECK_DUPLICATE_QR_HS: # Если False, то дубликаты разрешены
          logger.info("Проверка на дубликаты QR-кодов отключена для ХС. Возвращаем False.")
          return False
  else:
      logger.warning(f"Неизвестный тип покупки '{purchase_type}' при проверке дубликатов. По умолчанию проверяем.")

  try:
      history_file_path = _get_history_file_path(purchase_type)
      logger.info(f"Используется файл истории: {history_file_path}")

      # Если файл истории не существует, создаем его и считаем, что дубликатов нет.
      if not os.path.exists(history_file_path):
          logger.warning(f"Файл истории QR не найден: {history_file_path}. Создаем новый.")
          with open(history_file_path, 'w') as f:
              pass # Просто создаем пустой файл.
          return False

      # Читаем файл истории построчно и ищем совпадения QR-кода.
      with open(history_file_path, 'r') as f:
          for line in f:
              parts = line.strip().split(',')
              # QR-данные находятся в третьей части строки (индекс 2).
              if len(parts) >= 3 and parts[2] == qr_data:
                  logger.warning(f"Обнаружен дубликат QR-кода для {purchase_type}: '{qr_data}'")
                  return True # Найден дубликат.
      logger.info(f"QR-код '{qr_data}' не является дубликатом для {purchase_type}.")
      return False # Дубликат не найден.
  except IOError as e:
      logger.error(f"Ошибка чтения файла истории QR {history_file_path}: {e}")
      return False # В случае ошибки чтения файла, считаем, что дубликата нет.
  except ValueError as e:
      logger.error(f"Ошибка получения пути к файлу истории: {e}")
      return False
