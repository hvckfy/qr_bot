import os

BOT_TOKEN = "TOKEN"

ENABLE_LOGGING = True
LOG_FILE_PATH = "bot.log"

USE_EXTERNAL_API_QR = False

# Ключевые слова для внутренней валидации QR-кодов:
# QR-код ПравдаКофе должен начинаться с 'truecoffee'
PRAVDAKOFE_QR_KEYWORDS = {"truecoffee", "receipt", "coffee", "shop","pravdakofe"}
# QR-код ХС должен начинаться с 'hs'
HS_QR_KEYWORDS = {"hs", "loyalty", "bonus_receipt"}

# Настройки проверки дубликатов QR-кодов:
# Для ПравдаКофе (покупка кофе -> промокод ХС) - дубликаты запрещены (True), т.к. промокод выдается один раз.
CHECK_DUPLICATE_QR_PRAVDAKOFE = False
# Для ХС (покупка шмоток -> бонусы ПравдаКофе) - дубликаты разрешены (False), т.к. бонусы можно начислять несколько раз.
CHECK_DUPLICATE_QR_HS = False

QR_HISTORY_FILE_PRAVDAKOFE = "qr_history_pravdakofe.txt"
QR_HISTORY_FILE_HS = "qr_history_hs.txt"

# Файл для истории регистраций в программе лояльности ПравдаКофе.
PK_REGISTRATION_HISTORY_FILE = "registration_history_pravdakofe.txt"

USE_EXTERNAL_API_PROMOCODES = False
USE_FIXED_PROMOCODE = False
FIXED_PROMOCODE = "FIXEDPROMO123"
PROMOCODE_PREFIX = "PC15"

# URL для симуляции API лояльности ПравдаКофе.
PRAVDAKOFE_LOYALTY_API_URL = "http://api.pravdakofe-loyalty.com"

MSG_WELCOME = (
  "Где была сделана покупка?"
)
MSG_ASK_PHOTO = (
  "Отлично! Теперь отправьте мне фотографию вашего чека с QR-кодом."
)
MSG_NO_QR_FOUND = (
  "На изображении не найден QR-код. Пожалуйста, убедитесь, что QR-код четкий и хорошо виден."
)
MSG_DUPLICATE_QR = (
  "Этот QR-код уже был использован ранее. Пожалуйста, отправьте новый чек."
)
MSG_QR_VALIDATION_FAILED = (
  "QR-код не соответствует условиям проверки. Пожалуйста, проверьте чек."
)
MSG_ERROR_PROCESSING_PHOTO = (
  "Произошла ошибка при обработке вашей фотографии. Пожалуйста, попробуйте еще раз."
)
# Сообщение об успешном начислении бонусов для ПравдаКофе (выдается за покупку в ХС).
MSG_PRAVDAKOFE_BONUS_SUCCESS = (
  "Бонусы успешно начислены на вашу карту лояльности ПравдаКофе по номеру телефона {phone_number}. Спасибо за покупку!"
)
# Сообщение об успешной выдаче промокода для ХС (выдается за покупку в ПравдаКофе).
MSG_HS_PROMO_SUCCESS = (
  "Ваш промокод на 15% скидку: {promocode}. Спасибо за покупку!"
)
MSG_ERROR_REGISTRATION = (
  "Произошла ошибка при регистрации в системе лояльности ПравдаКофе. Пожалуйста, попробуйте еще раз или свяжитесь с поддержкой."
)
MSG_ASK_LOYALTY_CARD = (
  "У вас есть карта лояльности ПравдаКофе?"
)
MSG_ASK_PHONE_NUMBER = (
  "Пожалуйста, введите ваш номер телефона, привязанный к карте лояльности ПравдаКофе (например, +79XXXXXXXXX):"
)
MSG_ASK_REGISTRATION = (
  "У вас нет карты лояльности ПравдаКофе. Хотите зарегистрироваться? Для регистрации укажите ваше имя и номер телефона в формате: Имя, +79XXXXXXXXX"
)
MSG_REGISTRATION_SUCCESS = (
  "Спасибо за регистрацию, {name}! Ваш номер телефона {phone_number} сохранен. Теперь отправьте фотографию чека."
)
MSG_INVALID_REGISTRATION_FORMAT = (
  "Неверный формат. Пожалуйста, введите имя и номер телефона в формате: Имя, +79XXXXXXXXX"
)
MSG_INVALID_PHONE_FORMAT = (
  "Неверный формат номера телефона. Пожалуйста, введите номер в формате +79XXXXXXXXX."
)
