## 1. Что нам понадобится (Требования)

Прежде чем начать, убедись, что у тебя есть:
*   **Сервер на Ubuntu или Debian:** Я тестировал на них, так что с ними будет проще всего.
*   **Python 3.10:** Это прям **очень важно**. Мы с ним намучились, потому что `opencv-python` и `numpy` не очень дружат с новыми версиями Python (как 3.12, которая у меня была изначально). Так что ставим 3.10.
*   **Системные библиотеки:** Для работы с картинками и QR-кодами (OpenCV, Pyzbar).
*   **Git:** Если ты будешь клонировать репозиторий, а не просто копировать файлы.

## 2. Готовим сервер и ставим Python 3.10

Сначала обновим все, что есть, и поставим нужный Python.

### Если Python 3.10 нет в стандартных репах (скорее всего так и будет)

Мне пришлось добавить специальный репозиторий `deadsnakes`, чтобы получить Python 3.10. Делаем так:

\`\`\`bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
\`\`\`

### Теперь ставим сам Python 3.10 и все системные штуки

После добавления репозитория, можно смело ставить Python 3.10 и все библиотеки, которые нужны для OpenCV и Pyzbar. Это большой список, но лучше поставить все сразу:

\`\`\`bash
sudo apt install -y python3.10 python3.10-venv python3-dev python3-pip
sudo apt install -y libzbar0 libzbar-dev
sudo apt install -y libjpeg-dev libpng-dev libtiff-dev
sudo apt install -y libavcodec-dev libavformat-dev libswscale-dev
sudo apt install -y libgtk2.0-dev libcanberra-gtk-module
sudo apt install -y libxvidcore-dev libx264-dev
sudo apt install -y libopenexr-dev libatlas-base-dev
sudo apt install -y gfortran git
\`\`\`

## 3. Создаем отдельного пользователя для бота

Это хорошая практика для безопасности. Бот будет работать под своим пользователем, а не под `root`.

\`\`\`bash
sudo useradd -r -s /bin/false -d /opt/qr-receipt-bot bot
\`\`\`

## 4. Создаем папку и кидаем туда файлы бота

\`\`\`bash
# Создаем папку, где будет жить бот
sudo mkdir -p /opt/qr-receipt-bot

# Теперь копируем туда все файлы бота.
# Если ты сейчас на сервере, а файлы у тебя на компе, то сначала закинь их на сервер (например, через scp):
# scp -r /путь/к/твоему/боту/* user@your-server:/tmp/qr-receipt-bot/
# А потом на сервере:
sudo cp -r /tmp/qr-receipt-bot/* /opt/qr-receipt-bot/

# ИЛИ, если ты используешь Git (что удобнее для обновлений):
# sudo git clone https://github.com/твой-репозиторий.git /opt/qr-receipt-bot
\`\`\`

## 5. Настраиваем виртуальное окружение и ставим Python-зависимости

Это самый важный шаг, где мы решаем проблему с `numpy` и `opencv`.

\`\`\`bash
# Переходим в папку бота
cd /opt/qr-receipt-bot

# Создаем виртуальное окружение, указывая, что хотим Python 3.10
sudo python3.10 -m venv venv

# Активируем окружение и ставим зависимости.
# ВНИМАНИЕ: Порядок установки numpy и opencv-python-headless ОЧЕНЬ важен!
sudo venv/bin/pip install --upgrade pip
sudo venv/bin/pip install numpy==1.24.3             # Сначала ставим эту версию numpy
sudo venv/bin/pip install opencv-python-headless==4.8.1.78 # Потом эту версию opencv (headless - без графики, для сервера)
sudo venv/bin/pip install pyzbar==0.1.9
sudo venv/bin/pip install pyTelegramBotAPI==4.14.0

# Если у тебя есть requirements.txt, можешь использовать его после установки numpy и opencv:
# sudo venv/bin/pip install -r requirements.txt
\`\`\`

## 6. Настраиваем права доступа

Чтобы бот мог читать и писать в свою папку:

\`\`\`bash
sudo chown -R bot:bot /opt/qr-receipt-bot
sudo chmod +x /opt/qr-receipt-bot/bot.py
\`\`\`

## 7. Вставляем токен бота

Открываем конфиг и вставляем свой токен, который получили от @BotFather:

\`\`\`bash
sudo nano /opt/qr-receipt-bot/config.py

# Найди строку BOT_TOKEN и замени её на свой токен:
# BOT_TOKEN = "твой_реальный_токен_от_BotFather"
\`\`\`

## 8. Проверяем, что бот запускается вручную (ОЧЕНЬ ВАЖНО!)

Прежде чем мучиться с `systemd`, убедимся, что бот вообще работает. Если тут будет ошибка, то и `systemd` не поможет.

\`\`\`bash
# Запускаем бота от имени пользователя 'bot' из активированного окружения
sudo -u bot bash -c "source venv/bin/activate && python bot.py"
\`\`\`
Если все хорошо, ты увидишь сообщение "Бот запущен..." и никаких ошибок. Нажми `Ctrl+C`, чтобы остановить его. Если есть ошибки, смотри раздел "Решение распространенных проблем".

## 9. Создаем systemd сервис

Теперь, когда бот работает, сделаем из него системный сервис. Это позволит ему запускаться при старте сервера и автоматически перезапускаться, если что-то пойдет не так.

Создаем файл сервиса:

\`\`\`bash
sudo nano /etc/systemd/system/qr-receipt-bot.service
\`\`\`

Вставляем туда вот это содержимое:

\`\`\`ini
[Unit]
Description=QR Receipt Telegram Bot
After=network.target
Wants=network.target

[Service]
Type=simple
User=bot
Group=bot
WorkingDirectory=/opt/qr-receipt-bot
ExecStart=/opt/qr-receipt-bot/venv/bin/python /opt/qr-receipt-bot/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=qr-receipt-bot

Environment=PYTHONPATH=/opt/qr-receipt-bot
Environment=PYTHONUNBUFFERED=1

NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/qr-receipt-bot

MemoryMax=512M
CPUQuota=50%

[Install]
WantedBy=multi-user.target
\`\`\`

## 10. Запускаем сервис

\`\`\`bash
# Говорим systemd, что появился новый сервис
sudo systemctl daemon-reload

# Включаем автозапуск бота при загрузке системы
sudo systemctl enable qr-receipt-bot

# Запускаем бота!
sudo systemctl start qr-receipt-bot

# Проверяем статус, чтобы убедиться, что все ОК
sudo systemctl status qr-receipt-bot
\`\`\`
Если все хорошо, ты увидишь `Active: active (running)` зеленым цветом. Поздравляю, бот работает!

## 11. Как управлять ботом

Вот основные команды, которые тебе пригодятся:

### Основные команды:
\`\`\`bash
# Запустить бота
sudo systemctl start qr-receipt-bot

# Остановить бота
sudo systemctl stop qr-receipt-bot

# Перезапустить бота (удобно после изменений в коде)
sudo systemctl restart qr-receipt-bot

# Показать текущий статус бота
sudo systemctl status qr-receipt-bot

# Включить автозапуск бота при загрузке системы
sudo systemctl enable qr-receipt-bot

# Отключить автозапуск бота
sudo systemctl disable qr-receipt-bot
\`\`\`

### Как смотреть логи (если что-то пошло не так):
\`\`\`bash
# Показать все логи бота
sudo journalctl -u qr-receipt-bot

# Показать последние 50 строк логов
sudo journalctl -u qr-receipt-bot -n 50

# Показать логи в реальном времени (очень удобно для отладки, Ctrl+C для выхода)
sudo journalctl -u qr-receipt-bot -f

# Показать логи за сегодня
sudo journalctl -u qr-receipt-bot --since today

# Показать логи за последний час
sudo journalctl -u qr-receipt-bot --since "1 hour ago"
\`\`\`

## 12. Как обновлять бота

Когда ты внес изменения в код и хочешь обновить бота на сервере:

\`\`\`bash
# Останавливаем бота
sudo systemctl stop qr-receipt-bot

# Переходим в папку бота
cd /opt/qr-receipt-bot

# Обновляем код (если используешь git, это самый простой способ)
sudo -u bot git pull

# ИЛИ, если ты просто копировал файлы, то скопируй новые поверх старых:
# sudo cp -r /путь/к/новым/файлам/* /opt/qr-receipt-bot/
# (Убедись, что права остаются bot:bot)

# Если ты добавил новые библиотеки или изменил requirements.txt, обнови зависимости:
sudo -u bot /opt/qr-receipt-bot/venv/bin/pip install -r requirements.txt

# Запускаем бота обратно
sudo systemctl start qr-receipt-bot
\`\`\`

## 13. Решение распространенных проблем (что делать, если что-то пошло не так)

### Бот не запускается или падает с ошибкой:
1.  **Смотри логи!** Это первое, что нужно сделать. `sudo journalctl -u qr-receipt-bot --no-pager` покажет, почему он падает.
2.  **Проверь токен:** Убедись, что `BOT_TOKEN` в `config.py` правильный и без лишних пробелов.
3.  **Проверь права доступа:** `ls -la /opt/qr-receipt-bot/` и `sudo chown -R bot:bot /opt/qr-receipt-bot`.

### Ошибки с зависимостями (например, `numpy.core.multiarray failed to import` или `AttributeError: _ARRAY_API not found`):
Это та самая проблема с `numpy` и `opencv-python`, которую мы решали.
1.  **Убедись, что ты точно используешь Python 3.10.** Если нет, вернись к шагу 2.
2.  **Переустанови зависимости в правильном порядке и с указанными версиями:**
    \`\`\`bash
    cd /opt/qr-receipt-bot
    sudo rm -rf venv # Удаляем старое окружение, чтобы начать с чистого листа
    sudo python3.10 -m venv venv # Создаем новое с Python 3.10
    sudo -u bot /opt/qr-receipt-bot/venv/bin/pip install --upgrade pip
    sudo -u bot /opt/qr-receipt-bot/venv/bin/pip install numpy==1.24.3
    sudo -u bot /opt/qr-receipt-bot/venv/bin/pip install opencv-python-headless==4.8.1.78
    sudo -u bot /opt/qr-receipt-bot/venv/bin/pip install pyzbar==0.1.9
    sudo -u bot /opt/qr-receipt-bot/venv/bin/pip install pyTelegramBotAPI==4.14.0
    sudo chown -R bot:bot /opt/qr-receipt-bot # Снова права, на всякий случай
    \`\`\`

### Проблемы с правами доступа:
\`\`\`bash
sudo chown -R bot:bot /opt/qr-receipt-bot
sudo chmod +x /opt/qr-receipt-bot/bot.py
\`\`\`
