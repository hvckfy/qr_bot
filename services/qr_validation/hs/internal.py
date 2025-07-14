import logging
import config

if config.ENABLE_LOGGING:
  logger = logging.getLogger(__name__)
else:
  logger = logging.getLogger(__name__)
  logger.setLevel(logging.CRITICAL)

def validate(qr_data: str) -> bool:
  # Эта функция выполняет внутреннюю валидацию QR-кода для магазина "ХС".
  # Проверяет, начинается ли QR-код с 'hs' или содержит одно из предопределенных ключевых слов.
  logger.info(f"Внутренняя валидация данных QR-кода ХС: '{qr_data}'")
  qr_data_lower = qr_data.lower() # Приводим данные QR-кода к нижнему регистру для регистронезависимого поиска.

  # Проверяем, начинается ли QR-код с 'hs'
  if qr_data_lower.startswith("hs"):
      logger.info(f"Внутренняя валидация QR-кода ХС пройдена (начинается с 'hs').")
      return True

  # Проверяем наличие других ключевых слов
  for keyword in config.HS_QR_KEYWORDS:
      if keyword in qr_data_lower:
          logger.info(f"Внутренняя валидация QR-кода ХС пройдена (найдено ключевое слово: '{keyword}').")
          return True # Если найдено хотя бы одно ключевое слово, QR-код считается валидным.
  logger.warning("Внутренняя валидация QR-кода ХС не пройдена (ключевые слова не найдены и не начинается с 'hs').")
  return False # Если ни одно ключевое слово не найдено, QR-код невалиден.
