import logging
import config
from . import qr_detector
from . import qr_history_manager
from services.promocode_generation import internal as promocode_generator_internal
from services.promocode_generation import external as promocode_generator_external
from services.qr_validation.pc import internal as qr_validator_pc_internal
from services.qr_validation.pc import external as qr_validator_pc_external
from services.qr_validation.hs import internal as qr_validator_hs_internal
from services.qr_validation.hs import external as qr_validator_hs_external
from services.pk_api import loyalty as pk_loyalty_api # API лояльности для ПравдаКофе

if config.ENABLE_LOGGING:
  logger = logging.getLogger(__name__)
else:
  logger = logging.getLogger(__name__)
  logger.setLevel(logging.CRITICAL)

def process_receipt_image(image_path: str, user_id: int, purchase_type: str, loyalty_phone: str = None) -> str:
  # Главная функция, которая координирует весь процесс обработки чека.
  # Она отвечает за обнаружение QR, проверку на дубликаты, валидацию и выдачу результата.
  logger.info(f"Начало обработки изображения чека: {image_path} от пользователя {user_id} для покупки типа {purchase_type}.")

  # Шаг 1: Обнаружение и декодирование QR-кодов на изображении.
  qr_data_list = qr_detector.detect_and_decode_qr(image_path)

  if not qr_data_list:
      logger.info("QR-коды на изображении не найдены.")
      return config.MSG_NO_QR_FOUND

  # Обрабатываем каждый найденный QR-код (хотя обычно ожидается один).
  for qr_data in qr_data_list:
      # Шаг 2: Проверка на дубликат.
      # Используем менеджер истории, который учитывает настройки дублирования для каждого магазина.
      if qr_history_manager.is_qr_duplicate(qr_data, purchase_type):
          return config.MSG_DUPLICATE_QR

      is_valid_qr = False
      # Шаг 3: Валидация QR-кода.
      # Выбираем, использовать ли симуляцию внешнего API или внутреннюю логику валидации,
      # в зависимости от настроек в config.py и типа магазина.
      if config.USE_EXTERNAL_API_QR:
          if purchase_type == "pravdakofe":
              is_valid_qr = qr_validator_pc_external.validate(qr_data)
          elif purchase_type == "hs":
              is_valid_qr = qr_validator_hs_external.validate(qr_data)
          else:
              logger.error(f"Неизвестный тип покупки для внешней валидации: {purchase_type}")
              return config.MSG_ERROR_PROCESSING_PHOTO
      else:
          if purchase_type == "pravdakofe":
              is_valid_qr = qr_validator_pc_internal.validate(qr_data)
          elif purchase_type == "hs":
              is_valid_qr = qr_validator_hs_internal.validate(qr_data)
          else:
              logger.error(f"Неизвестный тип покупки для внутренней валидации: {purchase_type}")
              return config.MSG_ERROR_PROCESSING_PHOTO

      if is_valid_qr:
          # Шаг 4: Если QR-код прошел валидацию, записываем его в историю.
          # loyalty_phone передается только если это поток ХС (для лояльности ПравдаКофе).
          qr_history_manager.record_qr(user_id, qr_data, purchase_type, loyalty_phone if purchase_type == 'hs' else None) # Изменено условие

          # Шаг 5: Выполняем действие в зависимости от типа покупки.
          if purchase_type == "pravdakofe":
              # Для ПравдаКофе (покупка кофе) генерируем промокод ХС.
              promocode = ""
              if config.USE_FIXED_PROMOCODE:
                  promocode = config.FIXED_PROMOCODE
              elif config.USE_EXTERNAL_API_PROMOCODES:
                  promocode = promocode_generator_external.generate()
              else:
                  promocode = promocode_generator_internal.generate()
              logger.info(f"QR-код '{qr_data}' от пользователя {user_id} успешно обработан для ПравдаКофе. Выдан промокод ХС: {promocode}")
              return config.MSG_HS_PROMO_SUCCESS.format(promocode=promocode) # Используем сообщение для промокода ХС
          elif purchase_type == "hs":
              # Для ХС (покупка шмоток) отправляем бонусы на карту лояльности ПравдаКофе.
              if loyalty_phone:
                  if pk_loyalty_api.send_bonuses_to_user(user_id, loyalty_phone, 100): # Отправляем 100 бонусов.
                      logger.info(f"QR-код '{qr_data}' от пользователя {user_id} успешно обработан для ХС. Бонусы ПравдаКофе отправлены на телефон: {loyalty_phone}")
                      return config.MSG_PRAVDAKOFE_BONUS_SUCCESS.format(phone_number=loyalty_phone) # Используем сообщение для бонусов ПравдаКофе
                  else:
                      logger.error(f"Не удалось отправить бонусы через API ПравдаКофе для пользователя {user_id} (телефон: {loyalty_phone}).")
                      return config.MSG_ERROR_PROCESSING_PHOTO
              else:
                  logger.error(f"Покупка ХС обработана, но номер телефона лояльности ПравдаКофе не предоставлен для пользователя {user_id}.")
                  return config.MSG_ERROR_PROCESSING_PHOTO
          else:
              logger.error(f"Необработанный тип покупки после валидации: {purchase_type}")
              return config.MSG_ERROR_PROCESSING_PHOTO
      else:
          # Если QR-код не прошел валидацию.
          logger.warning(f"QR-код '{qr_data}' от пользователя {user_id} не прошел валидацию для {purchase_type}.")
          return config.MSG_QR_VALIDATION_FAILED

  # Если ни один из найденных QR-кодов не удалось обработать.
  return "Не удалось обработать ни один из найденных QR-кодов."
