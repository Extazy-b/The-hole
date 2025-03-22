from flask import Flask, request
import subprocess
from datetime import datetime
import json

app = Flask(__name__)

# Путь к лог-файлу
LOG_FILE = "/var/www/The_hole/webhook.log"

def log_message(message):
    """Записывает сообщение в лог-файл."""
    with open(LOG_FILE, "a") as log:
        log.write(f"{datetime.now()}: {message}\n")

@app.route('/webhook', methods=['POST'])
def webhook():
    # Логируем заголовки и тело запроса
    headers = dict(request.headers)
    payload = request.json

    log_message("Received webhook request")
    log_message(f"Headers: {json.dumps(headers, indent=2)}")
    log_message(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        # Выполняем git pull
        result = subprocess.run(
            ['git', '-C', '/var/www/The_hole', 'pull', 'origin', 'main'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Логируем результат
        log_message(f"Git pull stdout: {result.stdout}")
        log_message(f"Git pull stderr: {result.stderr}")

        if result.returncode == 0:
            log_message("Git pull successful")
            return 'OK', 200
        else:
            log_message(f"Git pull failed with code {result.returncode}")
            return 'Git pull failed', 500

    except Exception as e:
        # Логируем ошибку, если что-то пошло не так
        log_message(f"Error: {str(e)}")
        return 'Internal Server Error', 500

if __name__ == '__main__':
    # Запуск сервера на всех интерфейсах, порт 5000
    app.run(host='0.0.0.0', port=2020)
