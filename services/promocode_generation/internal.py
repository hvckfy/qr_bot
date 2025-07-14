import logging
import random
import string
import config

if config.ENABLE_LOGGING:
  logger = logging.getLogger(__name__)
else:
  logger = logging.getLogger(__name__)
  logger.setLevel(logging.CRITICAL)

def generate() -> str:
  # Эта функция генерирует промокод для ХС, используя внутреннюю логику.
  # Может вернуть фиксированный промокод или сгенерировать случайный.
  if config.USE_FIXED_PROMOCODE:
      # Если в конфиге указано использовать фиксированный промокод, возвращаем его.
      logger.info(f"Возвращаем фиксированный промокод: {config.FIXED_PROMOCODE}")
      return config.FIXED_PROMOCODE
  else:
      # Иначе генерируем случайный промокод из букв и цифр.
      logger.info("Внутренняя генерация промокода для ХС...")
      characters = string.ascii_uppercase + string.digits # Набор символов для промокода.
      promocode = config.PROMOCODE_PREFIX + ''.join(random.choice(characters) for i in range(5)) # Генерируем 10-значный код.
      logger.info(f"Сгенерирован внутренний промокод для ХС: {promocode}")
      return promocode
