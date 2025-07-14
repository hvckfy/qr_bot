import logging
import config

if config.ENABLE_LOGGING:
  logger = logging.getLogger(__name__)
else:
  logger = logging.getLogger(__name__)
  logger.setLevel(logging.CRITICAL)

def validate(qr_data: str) -> bool:
  # Эта функция выполняет внутреннюю валидацию QR-кода для магазина "ПравдаКофе".
  # Проверяет, начинается ли QR-код с 'truecoffee' или содержит одно из предопределенных ключевых слов.
  logger.info(f"Внутренняя валидация данных QR-кода ПравдаКофе: '{qr_data}'")
  qr_data_lower = qr_data.lower() # Приводим данные QR-кода к нижнему регистру.

  # Проверяем, начинается ли QR-код с 'truecoffee'
  if qr_data_lower.startswith("truecoffee"):
      logger.info(f"Внутренняя валидация QR-кода ПравдаКофе пройдена (начинается с 'truecoffee').")
      return True

  # Проверяем наличие других ключевых слов
  for keyword in config.PRAVDAKOFE_QR_KEYWORDS:
      if keyword in qr_data_lower:
          logger.info(f"Внутренняя валидация QR-кода ПравдаКофе пройдена (найдено ключевое слово: '{keyword}').")
          return True # Если найдено хотя бы одно ключевое слово, QR-код считается валидным.
  logger.warning("Внутренняя валидация QR-кода ПравдаКофе не пройдена (ключевые слова не найдены и не начинается с 'truecoffee').")
  return False # Если ни одно ключевое слово не найдено, QR-код невалиден.
