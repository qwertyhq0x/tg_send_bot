from telegram import Bot
from telegram.error import TelegramError
import time
import os
import re  # Импортируем модуль re

# Ваш токен бота (храните его в безопасном месте)
TOKEN = "YOUR_TOKEN"

def send_message_to_users(message_text, users_file, media_file=None, media_type=None, attach_text=False):
    # Создание экземпляра бота
    bot = Bot(token=TOKEN)

    # Замена символов \n на обычный перенос строки
    message_text = message_text.replace('\\n', '\n')

    # Открыть файл с ID пользователей
    try:
        with open(users_file, 'r') as file:
            users_ids = file.read().splitlines()
            if not users_ids:
                print("Файл с ID пользователей пуст.")
                return
    except FileNotFoundError:
        print(f"Файл {users_file} не найден.")
        return

    for user_id in users_ids:
        try:
            caption = message_text if attach_text else None

            # Отправка медиафайла, если он указан
            if media_file:
                with open(media_file, 'rb') as media:
                    if media_type == 'photo':
                        bot.send_photo(chat_id=user_id, photo=media, caption=caption, parse_mode='HTML')
                    elif media_type == 'animation':
                        bot.send_animation(chat_id=user_id, animation=media, caption=caption, parse_mode='HTML')
                    elif media_type == 'video':
                        bot.send_video(chat_id=user_id, video=media, caption=caption, parse_mode='HTML')

            # Отправка текстового сообщения, если текст не прикреплен к медиафайлу
            if not attach_text:
                bot.send_message(chat_id=user_id, text=message_text, parse_mode='HTML')

            time.sleep(1)  # Задержка между сообщениями, чтобы избежать ограничений Telegram
            print(f"Сообщение успешно отправлено пользователю {user_id}")

        except TelegramError as e:
            # Если это ошибка из-за ограничения по флуду
            if "Flood control exceeded" in e.message:
                # Извлекаем время ожидания из сообщения об ошибке
                wait_time = re.search(r"Retry in (\d+\.?\d*) seconds", e.message)
                if wait_time:
                    wait_time = float(wait_time.group(1))
                    print(f"Ограничение по флуду достигнуто. Ожидание {wait_time + 10} секунд перед следующей попыткой.")
                    time.sleep(wait_time + 10)  # добавляем 10 секунд на всякий случай
                else:
                    print(f"Ошибка при отправке сообщения пользователю {user_id}: {e.message}")
            else:
                # Вывести любую другую ошибку
                print(f"Ошибка при отправке сообщения пользователю {user_id}: {e.message}")

# Запустить функцию рассылки
while True:
    message_source = input("Выберите: ввести сообщение вручную (1) или выбрать файл с сообщением (2): ")
    if message_source in ['1', '2']:
        break
    print("Неверный выбор. Пожалуйста, введите 1 или 2.")

if message_source == '1':
    message_text = input("Напишите текст сообщения: ")
else:
    while True:
        message_file = input("Укажите путь к файлу с сообщением: ")
        if os.path.exists(message_file) and os.path.getsize(message_file) > 0:
            with open(message_file, 'r') as file:
                message_text = file.read().strip()
                if message_text:
                    break
                else:
                    print("Файл пустой.")
        else:
            print(f"Файл {message_file} не найден.")

while True:
    users_file = input("Укажите файл с ID пользователей: ")
    if os.path.exists(users_file) and os.path.getsize(users_file) > 0:
        break
    print(f"Файл {users_file} не найден или пуст.")

media_file = input("Укажите путь к медиафайлу или оставьте пустым: ")
media_type = None
attach_text = False

if media_file:
    while True:
        media_choice = input("Выберите тип медиафайла: фото (1), анимация (2), видео (3): ")
        if media_choice in ['1', '2', '3']:
            media_type = 'photo' if media_choice == '1' else 'animation' if media_choice == '2' else 'video'
            break
        print("Неверный выбор. Пожалуйста, введите 1, 2 или 3.")

    attach_choice = input("Прикрепить текст к медиафайлу? (да/нет): ")
    attach_text = attach_choice.lower() == 'да'

    if attach_text and len(message_text) > 500:
        print("Текст слишком длинный для прикрепления к медиафайлу (более 500 символов). Пожалуйста, введите текст заново.")
        message_text = input("Напишите текст сообщения: ")

send_message_to_users(message_text, users_file, media_file, media_type, attach_text)
