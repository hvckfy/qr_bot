import logging
import time
import config

if config.ENABLE_LOGGING:
  logger = logging.getLogger(__name__)
else:
  logger = logging.getLogger(__name__)
  logger.setLevel(logging.CRITICAL)

def generate() -> str:
  # Эта функция симулирует обращение к внешнему API для генерации промокода для ХС.
  # В реальном проекте здесь был бы HTTP-запрос к серверу промокодов.
  logger.info("Используем внешний API для генерации промокода для ХС...")
  time.sleep(1) # Имитируем задержку сетевого запроса.
  logger.info("Симуляция генерации внешнего промокода для ХС завершена.")
  return "EXTERNALPROMO15" # Возвращаем фиксированный промокод для симуляции.
