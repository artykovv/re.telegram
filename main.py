import os
import telebot
import requests


bot = telebot.TeleBot('7067149281:AAGTfjDFxeFJQdhV76zL3QYPfDTsCr1rOWM')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, "Для записи нового товара надо нажать кнопку отправтиь файл")
    bot.send_message(message.from_user.id, "Файл должен быть в формате xlsx")
    bot.send_message(message.from_user.id, "Для получение команда /get")


@bot.message_handler(content_types=['document'])
def handle_file(message):
    file_info = bot.get_file(message.document.file_id)
    file_url = f'https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}'
    
    try:
        # Создаем директорию temp, если ее нет
        if not os.path.exists('temp'):
            os.makedirs('temp')

        # Получаем полный путь к временному файлу
        temp_file_path = f"temp/{message.document.file_name}"

        # Скачиваем файл по URL и сохраняем его во временный файл
        response = requests.get(file_url)
        with open(temp_file_path, 'wb') as f:
            f.write(response.content)

        # Отправляем файл на сервер FastAPI
        files = {'file': open(temp_file_path, 'rb')}
        response = requests.post('https://re-production.up.railway.app/api/v1/products/upload', files=files)

        if response.status_code == 200:
            bot.send_message(message.chat.id, "Файл успешно загружен и база данных обновлена.")
        else:
            bot.send_message(message.chat.id, "Ошибка при загрузке файла.")

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при загрузке файла: {e}")


@bot.message_handler(commands=['get'])
def get_all_products(message):
    try:
        # Выполняем GET-запрос к серверу FastAPI для получения файла Excel
        response = requests.get('https://re-production.up.railway.app/api/v1/products/get/all')

        if response.status_code == 200:
            # Создаем временный файл для сохранения содержимого файла Excel
            temp_file_path = 'temp/products.xlsx'
            with open(temp_file_path, 'wb') as f:
                f.write(response.content)

            # Отправляем полученный файл пользователю
            with open(temp_file_path, 'rb') as f:
                bot.send_document(message.chat.id, f, caption="Ваши продукты в формате Excel")

            # Удаляем временный файл после отправки
            os.remove(temp_file_path)

        else:
            bot.send_message(message.chat.id, "Ошибка при получении данных о продуктах.")

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при выполнении запроса: {e}")

bot.polling(none_stop=True, interval=0)
