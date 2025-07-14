import cv2
from pyzbar.pyzbar import decode
import logging
import config

if config.ENABLE_LOGGING:
  logger = logging.getLogger(__name__)
else:
  logger = logging.getLogger(__name__)
  logger.setLevel(logging.CRITICAL)

def detect_and_decode_qr(image_path: str) -> list[str]:
  # Функция для обнаружения и декодирования QR-кодов на изображении.
  logger.info(f"Попытка обнаружения QR-кодов на изображении: {image_path}")
  try:
    # Загружаем изображение с помощью библиотеки OpenCV.
    image = cv2.imread(image_path)
    if image is None:
        logger.error(f"Не удалось загрузить изображение по пути: {image_path}")
        return []

    # Используем библиотеку pyzbar для поиска и декодирования QR-кодов.
    decoded_objects = decode(image)
    # Извлекаем данные из каждого найденного QR-кода и декодируем их в UTF-8.
    qr_data_list = [obj.data.decode('utf-8') for obj in decoded_objects]

    if qr_data_list:
        logger.info(f"Обнаружены QR-коды: {qr_data_list}")
    else:
        logger.info("QR-коды не обнаружены.")

    return qr_data_list
  except Exception as e:
    # Логируем любые ошибки, возникшие в процессе обнаружения/декодирования.
    logger.error(f"Ошибка обнаружения/декодирования QR-кодов: {e}")
    return []
