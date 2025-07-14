import logging
import os
import telebot
from telebot import types
import config
from core import main_processor
import re
from services.pk_api import loyalty as pk_loyalty_api # API лояльности для ПравдаКофе

# Настраиваем логирование для отслеживания работы бота.
# Если в конфиге включено логирование, сообщения будут записываться в файл и выводиться в консоль.
if config.ENABLE_LOGGING:
  logging.basicConfig(
      level=logging.INFO,
      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
      handlers=[
          logging.FileHandler(config.LOG_FILE_PATH),
          logging.StreamHandler()
      ]
  )
  logger = logging.getLogger(__name__)
else:
  # Если логирование отключено, устанавливаем критический уровень, чтобы ничего не выводилось.
  logger = logging.getLogger(__name__)
  logger.setLevel(logging.CRITICAL)

# Проверяем, установлен ли токен бота. Без него бот не сможет подключиться к Telegram.
if not config.BOT_TOKEN or config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
    logger.critical("Токен бота не установлен в config.py. Пожалуйста, обновите config.py.")
    print("Ошибка: Токен бота не установлен в config.py. Пожалуйста, обновите config.py.")
    exit()

# Инициализируем объект бота с полученным токеном.
bot = telebot.TeleBot(config.BOT_TOKEN)

# Словарь для хранения текущего состояния каждого пользователя.
# Это нужно, чтобы бот "помнил", на каком этапе диалога находится пользователь.
user_states = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
  # Обработчик команды /start. Приветствует пользователя и предлагает выбрать тип покупки.
  logger.info(f"Получена команда /start от пользователя {message.from_user.id}")
  # Создаем кнопки для выбора магазина.
  markup = types.InlineKeyboardMarkup()
  btn_pravdakofe = types.InlineKeyboardButton("ПравдаКофе", callback_data="purchase_pravdakofe")
  btn_hs = types.InlineKeyboardButton("ХС", callback_data="purchase_hs")
  markup.add(btn_pravdakofe, btn_hs)
  # Отправляем приветственное сообщение с кнопками.
  bot.reply_to(message, config.MSG_WELCOME, reply_markup=markup)
  # Инициализируем состояние пользователя.
  user_states[message.from_user.id] = {'flow': None}

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
  # Обработчик нажатий на инлайн-кнопки.
  user_id = call.from_user.id
  message_id = call.message.message_id
  chat_id = call.message.chat.id

  if call.data == "purchase_pravdakofe":
      # Пользователь выбрал "ПравдаКофе". Сразу просим фото чека для получения промокода ХС.
      user_states[user_id] = {'flow': 'pravdakofe', 'awaiting_photo': True}
      bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=config.MSG_ASK_PHOTO)
      logger.info(f"Пользователь {user_id} выбрал поток ПравдаКофе. Сразу просим фото чека для получения промокода ХС.")
  elif call.data == "purchase_hs":
      # Пользователь выбрал "ХС". Спрашиваем о наличии карты лояльности ПравдаКофе для начисления бонусов.
      user_states[user_id] = {'flow': 'hs', 'awaiting_photo': False}
      markup = types.InlineKeyboardMarkup()
      btn_yes = types.InlineKeyboardButton("Да", callback_data="hs_loyalty_yes") # Новое имя колбэка
      btn_no = types.InlineKeyboardButton("Нет", callback_data="hs_loyalty_no") # Новое имя колбэка
      markup.add(btn_yes, btn_no)
      bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=config.MSG_ASK_LOYALTY_CARD, reply_markup=markup)
      logger.info(f"Пользователь {user_id} выбрал поток ХС, спрашиваем о карте лояльности ПравдаКофе.")
  elif call.data == "hs_loyalty_yes": # Обработка для потока ХС -> лояльность ПравдаКофе
      # Пользователь подтвердил наличие карты лояльности ПравдаКофе. Запрашиваем номер телефона.
      user_states[user_id]['flow'] = 'hs_ask_phone' # Новое состояние
      bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=config.MSG_ASK_PHONE_NUMBER)
      logger.info(f"У пользователя {user_id} есть карта лояльности ПравдаКофе, запрашиваем номер телефона для потока ХС.")
  elif call.data == "hs_loyalty_no": # Обработка для потока ХС -> лояльность ПравдаКофе
      # Пользователь не имеет карты лояльности ПравдаКофе. Предлагаем регистрацию.
      user_states[user_id]['flow'] = 'hs_ask_registration' # Новое состояние
      bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=config.MSG_ASK_REGISTRATION)
      logger.info(f"У пользователя {user_id} нет карты лояльности ПравдаКофе, предлагаем регистрацию для потока ХС.")

  # Отвечаем на callback-запрос, чтобы кнопка перестала быть "нажатой".
  bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('flow') in ['hs_ask_phone', 'hs_ask_registration'])
def handle_loyalty_info_input(message):
  # Обработчик текстовых сообщений, когда бот ожидает номер телефона или данные для регистрации в потоке ХС (для лояльности ПравдаКофе).
  user_id = message.from_user.id
  current_flow = user_states[user_id]['flow']
  text = message.text.strip()

  if current_flow == 'hs_ask_phone':
      # Если ожидаем номер телефона для существующей карты ПравдаКофе.
      if re.fullmatch(r'^\+?\d{10,15}$', text): # Проверяем формат номера телефона.
          user_states[user_id]['loyalty_phone'] = text
          user_states[user_id]['flow'] = 'hs_awaiting_photo' # Переходим к ожиданию фото.
          bot.reply_to(message, config.MSG_ASK_PHOTO)
          logger.info(f"Пользователь {user_id} предоставил номер телефона: {text}. Ожидаем фото для потока ХС.")
      else:
          bot.reply_to(message, config.MSG_INVALID_PHONE_FORMAT)
          logger.warning(f"Пользователь {user_id} предоставил неверный формат телефона: {text}")
  elif current_flow == 'hs_ask_registration':
      # Если ожидаем имя и телефон для регистрации в ПравдаКофе.
      parts = text.split(',', 1) # Разделяем ввод на имя и телефон по первой запятой.
      if len(parts) == 2:
          name = parts[0].strip()
          phone = parts[1].strip()
          if re.fullmatch(r'^\+?\d{10,15}$', phone): # Проверяем формат номера телефона.
              # Симулируем регистрацию пользователя через API лояльности ПравдаКофе.
              if pk_loyalty_api.register_user(name, phone):
                  user_states[user_id]['registration_name'] = name
                  user_states[user_id]['loyalty_phone'] = phone
                  user_states[user_id]['flow'] = 'hs_awaiting_photo' # Переходим к ожиданию фото.
                  bot.reply_to(message, config.MSG_REGISTRATION_SUCCESS.format(name=name, phone_number=phone))
                  logger.info(f"Пользователь {user_id} зарегистрирован с именем: {name}, телефоном: {phone}. Ожидаем фото для потока ХС.")
              else:
                  bot.reply_to(message, config.MSG_ERROR_REGISTRATION)
                  logger.error(f"Не удалось зарегистрировать пользователя {user_id} с именем: {name}, телефоном: {phone}")
                  user_states[user_id] = {'flow': None} # Сбрасываем состояние в случае ошибки.
          else:
              bot.reply_to(message, config.MSG_INVALID_PHONE_FORMAT)
              logger.warning(f"Пользователь {user_id} предоставил неверный формат телефона при регистрации: {phone}")
      else:
          bot.reply_to(message, config.MSG_INVALID_REGISTRATION_FORMAT)
          logger.warning(f"Пользователь {user_id} предоставил неверный формат регистрации: {text}")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
  # Обработчик входящих фотографий. Это ключевой момент для обработки чеков.
  user = message.from_user
  user_id = user.id
  logger.info(f"Пользователь {user.full_name} ({user_id}) отправил фото.")

  user_state = user_states.get(user_id, {})
  current_flow = user_state.get('flow')
  loyalty_phone = user_state.get('loyalty_phone') # Номер телефона для лояльности (если есть).

  # Проверяем, находится ли пользователь в состоянии, когда ожидается фото.
  if current_flow not in ['pravdakofe', 'hs_awaiting_photo']: # Обновленные состояния
      bot.reply_to(message, "Пожалуйста, сначала выберите тип покупки, используя команду /start.")
      logger.warning(f"Пользователь {user_id} отправил фото без инициации соответствующего потока. Текущее состояние: {current_flow}")
      return

  # Проверяем, что сообщение действительно содержит фото.
  if not message.photo:
      logger.warning(f"Сообщение от {user_id} не содержит фото.")
      bot.reply_to(message, "Пожалуйста, отправьте фотографию.")
      return

  # Получаем информацию о файле фото и формируем временный путь для сохранения.
  file_info = bot.get_file(message.photo[-1].file_id)
  temp_photo_path = f"temp_photo_{file_info.file_id}.jpg"

  try:
      # Скачиваем фото и сохраняем его во временный файл.
      downloaded_file = bot.download_file(file_info.file_path)
      with open(temp_photo_path, 'wb') as new_file:
          new_file.write(downloaded_file)
      logger.info(f"Фото сохранено во временный файл: {temp_photo_path}")

      # Определяем тип покупки для передачи в основной процессор.
      purchase_type_for_processor = None
      if current_flow == 'pravdakofe': # Если выбран поток ПравдаКофе (для промокода ХС)
          purchase_type_for_processor = 'pravdakofe'
      elif current_flow == 'hs_awaiting_photo': # Если выбран поток ХС (для лояльности ПравдаКофе)
          purchase_type_for_processor = 'hs'

      if purchase_type_for_processor:
          # Вызываем основной процессор для обработки чека.
          # loyalty_phone передается только если это поток ХС (для лояльности ПравдаКофе).
          result_message = main_processor.process_receipt_image(
              temp_photo_path, user_id, purchase_type_for_processor,
              loyalty_phone if purchase_type_for_processor == 'hs' else None # Изменено условие
          )
          bot.reply_to(message, result_message)
          logger.info(f"Ответ пользователю {user_id}: {result_message}")
      else:
          # Если тип покупки не определен, это ошибка.
          bot.reply_to(message, config.MSG_ERROR_PROCESSING_PHOTO)
          logger.error(f"Не удалось определить тип покупки для пользователя {user_id} из состояния: {user_state}")

  except Exception as e:
      # Ловим любые ошибки при обработке фото.
      logger.error(f"Ошибка обработки фото от пользователя {user_id}: {e}", exc_info=True)
      bot.reply_to(message, config.MSG_ERROR_PROCESSING_PHOTO)
  finally:
      # В любом случае, удаляем временный файл и сбрасываем состояние пользователя.
      if os.path.exists(temp_photo_path):
          os.remove(temp_photo_path)
          logger.info(f"Временный файл удален: {temp_photo_path}")
      user_states[user_id] = {'flow': None}

def main() -> None:
  # Главная функция для запуска бота.
  logger.info("Бот запущен. Нажмите Ctrl+C для остановки.")
  print("Бот запущен. Нажмите Ctrl+C для остановки.")
  # Запускаем опрос Telegram-серверов на наличие новых сообщений.
  bot.polling(none_stop=True)

if __name__ == "__main__":
  main()
