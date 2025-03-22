from flask import Flask, request
import subprocess
import logging
from logging.handlers import RotatingFileHandler
import json

app = Flask(__name__)

# Настройка логирования
LOG_FILE = "/home/serotonin/The_hole/logs/webhooks/webhook.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler(LOG_FILE, maxBytes=10485760, backupCount=5),  # 10 MB на файл, 5 бэкапов
        logging.StreamHandler()  # Вывод в консоль
    ]
)
logger = logging.getLogger(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    # Логируем заголовки и тело запроса
    headers = dict(request.headers)
    payload = request.json

    logger.info("Received webhook request")
    logger.debug(f"Headers: {json.dumps(headers, indent=2)}")
    logger.debug(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        # Выполняем git pull
        result = subprocess.run(
            ['git', '-C', '/var/www/The_hole', 'pull', 'origin', 'main'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Логируем результат
        logger.info(f"Git pull stdout: {result.stdout}")
        if result.stderr:
            logger.error(f"Git pull stderr: {result.stderr}")

        if result.returncode == 0:
            logger.info("Git pull successful")
            return 'OK', 200
        else:
            logger.error(f"Git pull failed with code {result.returncode}")
            return 'Git pull failed', 500

    except Exception as e:
        # Логируем ошибку, если что-то пошло не так
        logger.error(f"Error: {str(e)}", exc_info=True)
        return 'Internal Server Error', 500

if __name__ == '__main__':
    # Запуск сервера на всех интерфейсах, порт 5000
    app.run(host='0.0.0.0', port=2020)