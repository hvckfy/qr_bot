import logging
import time
import config

if config.ENABLE_LOGGING:
  logger = logging.getLogger(__name__)
else:
  logger = logging.getLogger(__name__)
  logger.setLevel(logging.CRITICAL)

def validate(qr_data: str) -> bool:
  # Эта функция симулирует валидацию QR-кода для магазина "ХС" через внешний API.
  # В реальном приложении здесь был бы запрос к API системы ХС.
  logger.info(f"Используем внешний API для валидации QR-кода ХС: '{qr_data}'...")
  time.sleep(1) # Имитируем задержку сетевого запроса.
  logger.info("Симуляция внешней валидации QR-кода ХС завершена и пройдена.")
  return True # Для симуляции всегда возвращаем True, что означает успешную валидацию.
