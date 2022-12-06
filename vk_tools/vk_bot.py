#

from random import randrange
from pprint import pprint

import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from config import get_bot_config
from vk_tools.matchmaker import Matchmaker


def converter(string=' ', splitter=','):
    return list(c.strip() for c in string.strip().split(splitter))


class VkBot(Matchmaker):
    def __init__(self, bot: str = 'bot.cfg'):
        super(VkBot, self).__init__()
        self._BOT_CONFIG = get_bot_config(bot)
        self.is_advanced = False
        self.service = self._BOT_CONFIG['mode']['start-up']
        self.vk_session = vk_api.VkApi(token=self._BOT_CONFIG['token'])
        self.vk_api = self.vk_session.get_api()
        self.vk_tools = vk_api.VkTools(self.vk_session)
        print(f"Создан объект бота! (id={self.vk_session.app_id})")

    def change_mode(self, mode=''):
        self.is_advanced = not self.is_advanced
        self.service = mode if self.is_advanced else self._BOT_CONFIG['mode']['start-up']
        return self.service

    def get_group_users(self) -> list:
        return self.vk_tools.get_all('groups.getMembers', 1000, {'group_id': self._BOT_CONFIG['group_id']})['items']

    def matchmaker_mode(self, event):
        self.send_msg(event, 'Спасибо за компанию!')

    def start(self):
        # Работа с сообщениями
        greetings = converter(self._BOT_CONFIG['greetings'])
        farewells = converter(self._BOT_CONFIG['farewells'])
        while True:
            longpoll = VkLongPoll(self.vk_session, group_id=self._BOT_CONFIG['group_id'])
            print('Запущен бот группы id =', longpoll.group_id)
            try:
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        self.print_message_description(event)
                        text = event.text.lower()
                        # Oтветы:
                        if text in greetings and not self.is_advanced:
                            keyboard = VkKeyboard(one_time=True)
                            keyboard.add_button(self.service['services']['matchmaker']['button'],
                                                VkKeyboardColor.PRIMARY)
                            greeting = greetings[randrange(len(greetings))]
                            self.send_msg(event, f'{greeting.upper()},\n'
                                                 f'{self.get_user_name(event.user_id)}!\n :))',
                                          keyboard)
                        elif text in farewells and not self.is_advanced:
                            farewell = farewells[randrange(len(farewells))]
                            self.send_msg(event, f'{farewell.upper()},\n'
                                                 f'{self.get_user_name(event.user_id)}!\n :))')
                        elif text == self.service['services']['matchmaker']['command'].lower() \
                                or text == self.service['services']['matchmaker']['button'].lower() \
                                and not self.is_advanced:
                            self.change_mode(self.service['services']['matchmaker'])
                            self.matchmaker_mode(event)
                            self.change_mode()
                        else:
                            self.send_msg(event, 'Не понимаю...')
            except requests.exceptions.ReadTimeout as timeout:
                print(timeout)
                continue

    def send_msg(self, event, message, keyboard=None):
        """" Получает id пользователя ВК <user_id>, и сообщение ему """
        service_msg = self.send_msg_title()
        for service in self.service['services']:
            activity = self.service['services'][service]
            service_msg += "\n-\t{}\t(\t{}\t)".format(activity['button'].upper(), activity['command'])
        post = {'peer_id': event.peer_id, 'message': message + service_msg, 'random_id': get_random_id()}
        if keyboard:
            post['keyboard'] = keyboard.get_keyboard()
        try:
            self.vk_session.method('messages.send', post)
        except vk_api.exceptions.ApiError as no_permission:
            print(f'\t{no_permission}')

    def send_msg_title(self):
        comment = f'\n*\t{self.service["description"].strip().lower()}\t*' if self.service['description'] else ''
        return "\nсервис {}:{}".format(self.service['button'].upper(), comment)

    def print_message_description(self, event):
        msg = 'Новое сообщение:\t'
        msg += 'личное' if event.user_id > 0 else ''
        msg += f'из чата {event.chat_id}' if event.from_chat else ''
        msg += f'\nот: {self.get_user_title(event.user_id)})'
        msg += f' *--- {event.text}'
        print(msg)
        # print('*---', event.from_user, event.from_chat, event.from_group, event.from_me)
        return msg

    def get_user(self, user_id, name_case='nom', fields="city"):
        """ Получаем пользователя """
        return self.vk_api.users.get(user_ids=user_id, fields=fields, name_case=name_case)[0]

    def get_user_name(self, user_id, name_case='nom'):
        """ Получаем имя пользователя"""
        user = self.get_user(user_id, name_case)
        return f'{user["first_name"]} {user["last_name"]}'

    def get_user_city(self, user_id):
        """ Получаем город пользователя"""
        user = self.get_user(user_id)
        return user["city"]["title"]

    def get_user_title(self, user_id):
        """ Получаем кратко пользователя"""
        user = self.get_user(user_id, 'gen')
        return f'{user["last_name"]} {user["first_name"]} (id = {user_id})'
        #        f'{user["city"]["title"]} (id = {user_id})'

