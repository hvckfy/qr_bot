import logging
import time
import config
import os
import datetime

if config.ENABLE_LOGGING:
  logger = logging.getLogger(__name__)
else:
  logger = logging.getLogger(__name__)
  logger.setLevel(logging.CRITICAL)

def _get_registration_history_file_path() -> str:
  # Вспомогательная функция для определения пути к файлу истории регистраций ПравдаКофе.
  base_dir = os.path.dirname(os.path.abspath(__file__))
  # Путь к файлу находится на два уровня выше текущей директории.
  return os.path.join(base_dir, '..', '..', config.PK_REGISTRATION_HISTORY_FILE)

def register_user(name: str, phone: str) -> bool:
  # Эта функция симулирует регистрацию нового пользователя в системе лояльности ПравдаКофе.
  # В реальном проекте здесь был бы HTTP-запрос к API регистрации.
  logger.info(f"Попытка регистрации пользователя '{name}' с телефоном '{phone}' через API ПравдаКофе.")
  time.sleep(0.5) # Имитируем задержку сетевого запроса.

  try:
      history_file_path = _get_registration_history_file_path()
      timestamp = datetime.datetime.now().isoformat() # Получаем текущее время.
      # Записываем данные о регистрации в отдельный файл истории.
      with open(history_file_path, 'a') as f:
          f.write(f"{timestamp},{name},{phone}\n")
      logger.info(f"Пользователь '{name}' с телефоном '{phone}' успешно зарегистрирован и запись добавлена в {config.PK_REGISTRATION_HISTORY_FILE}.")
      return True # Симуляция успешной регистрации.
  except IOError as e:
      logger.error(f"Ошибка записи регистрации в файл истории {history_file_path}: {e}")
      return False # Ошибка при записи в файл.
  except Exception as e:
      logger.error(f"Непредвиденная ошибка при записи регистрации: {e}")
      return False # Любая другая непредвиденная ошибка.

def send_bonuses_to_user(user_id: int, phone: str, amount: int) -> bool:
  # Эта функция симулирует начисление бонусов пользователю через API лояльности ПравдаКофе.
  # В реальном проекте здесь был бы HTTP-запрос к API начисления бонусов.
  logger.info(f"Симуляция отправки {amount} бонусов пользователю {user_id} (телефон: {phone}) через API ПравдаКофе...")
  time.sleep(0.7) # Имитируем задержку сетевого запроса.
  logger.info(f"{amount} бонусов симулированы как отправленные пользователю {user_id} (телефон: {phone}) через API ПравдаКофе.")
  return True # Симуляция успешной отправки бонусов.
