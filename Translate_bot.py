import datetime
import os
import requests
import time
import translators as ts
from langdetect import detect
from ..token import TOKEN

URL = 'https://api.telegram.org/bot' + TOKEN


class TelegramTranslateBot():
    def __init__(self):
        self.message_list = self.get_update()
        self.target_language = 'en'
        # ID        
        self.old_update_id = self.get_update_id()
        self.update_id = None
        self.chat_id = None
        self.message_id = None
        self.user_id = None

        # DATA
        self.user_name = None
        self.message_text = None
        self.message_language = None

        while True:
            time.sleep(2)
            self.message_list = self.get_update()

            # проверяем есть ли новое сообщение
            if self.check_message():
                self.parse_message()
                if self.check_translate():
                    self.send_message(self.chat_id, ts.google(self.message_text))
                    self.log_message()
                    # print(f'Имя пользователя: {first_name}, сообщение: {text}')

    def get_update(self):
        """ получаем json с входящими сообщениями """
        message_list = requests.get(URL + '/getUpdates?offset=-1').json()
        return message_list.get('result')[0]  # получаем текущий элемент из обновлений

    def get_update_id(self):
        return self.message_list['update_id']

    def check_message(self):
        """ проверяем новое ли сообщение """
        self.update_id = self.get_update_id()
        if self.old_update_id < self.update_id:
            return True

    def parse_message(self):
        """ обновляем id и переменные сообщения """
        # list of data
        message_list = self.message_list.get('message') \
            if self.message_list.get('message') \
            else self.message_list.get('my_chat_member')

        # ID        
        self.old_update_id = self.update_id  # обновляем id сообщения
        self.chat_id = message_list.get('chat').get('id')
        self.message_id = message_list.get('message_id')
        self.user_id = message_list.get('from').get('id')

        # DATA
        self.user_name = message_list.get('from').get('first_name')
        self.message_text = message_list.get('text')

    def check_translate(self):
        """ проверяет неоходимость провекри """
        # Проверяет является ли целевым языком (Русский - True)
        if detect(self.message_text) != self.target_language:
            alphabet = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
            # Если есть русские буквы (Русский - True)
            return not alphabet.isdisjoint(self.message_text.lower())

    def send_message(self, chat_id, text=None):
        """ отправить сообщение от бота """
        requests.get(URL + '/sendMessage', data={
            'chat_id': chat_id,
            'text': text,
        })

    def log_message(self):
        with open(os.path.relpath('TranslateBot_log', start=os.curdir), 'a', encoding='utf-8') as file:
            log = '{} {:>15} {:>10}\n'.format(datetime.datetime.now(), self.user_name, self.user_id)
            file.write(log)

if __name__ == '__main__':
    bot = TelegramTranslateBot()
