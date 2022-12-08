#

from random import randrange
from pprint import pprint

import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from config import get_bot_config
from vk_tools.vk_bot_menu import VkBotMenu
from vk_tools.matchmaker import Matchmaker


def converter(string=' ', splitter=','):
    return list(c.strip() for c in string.strip().split(splitter))


class VkBot(Matchmaker):
    def __init__(self, bot: str = 'bot.cfg'):
        super(VkBot, self).__init__()
        self._BOT_CONFIG = get_bot_config(bot)
        self.menu = VkBotMenu(self._BOT_CONFIG['mode'])
        self.polite = None
        self.vk_session = vk_api.VkApi(token=self._BOT_CONFIG['token'])
        self.vk_api = self.vk_session.get_api()
        self.vk_tools = vk_api.VkTools(self.vk_session)
        print(f"Создан объект бота! (id={self.vk_session.app_id})")

    def get_group_users(self) -> list:
        return self.vk_tools.get_all('groups.getMembers', 1000, {'group_id': self._BOT_CONFIG['group_id']})['items']

    def start(self):
        # Работа с сообщениями
        greetings = converter(self._BOT_CONFIG['greetings'])
        farewells = converter(self._BOT_CONFIG['farewells'])
        while True:
            longpoll = VkLongPoll(self.vk_session, group_id=self._BOT_CONFIG['group_id'])
            print('Запущен бот группы id =', longpoll.group_id)
            try:
                for event in longpoll.listen():
                    if self.menu.service_name == 'start-up':
                        self.start_mode_events(event)
                    elif self.menu.service_name == 'matchmaker':
                        self.matchmaker_mode_events(event)
                    elif self.menu.service_name == 'search':
                        self.start_mode_events(event)
                    elif self.menu.service_name == 'print':
                        self.start_mode_events(event)
                    elif self.menu.service_name == 'exit' and self.menu.service_code == '113':
                        self.start_mode_events(event)
                    else:
                        self.start_mode_events(event)
            except requests.exceptions.ReadTimeout as timeout:
                continue

    def search_mode_events(self, event):
        pass

    def print_mode_events(self, event):
        pass

    def exit_mode_events(self, event):
        pass

    def matchmaker_mode_start(self, event, message=''):
        self.polite = None
        keyboard = VkKeyboard(one_time=True)
        for button in self.menu.get_button_list():
            keyboard.add_button(button, VkKeyboardColor.PRIMARY)
        self.send_msg(event, f'{message} Текущий', keyboard)

    def matchmaker_mode_events(self, event):
        greetings = converter(self._BOT_CONFIG['greetings'])
        farewells = converter(self._BOT_CONFIG['farewells'])
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            self.print_message_description(event)
            text = event.text.lower()
            self.polite = None
            # Oтветы:
            if (text == self.menu.services['exit']['command'].lower()
                    or text == self.menu.services['exit']['button'].lower()):
                if event.from_chat:
                    self.polite = 'switching'
                    message = f'{self.get_user_name(event.user_id)}!\n'
                    self.send_msg(event, '{}Юзать сервис переходи в чат с @{}!'.format(
                        message, self._BOT_CONFIG["name"]))
                else:
                    message = '{},\nсервис "{}" закрыт!'.format(
                        self.get_user_name(event.user_id), self.menu.service_name)
                    self.menu.exit()
                    self.start_mode_start(event, message)
                    # keyboard = VkKeyboard(one_time=True)
                    # for button in self.menu.get_button_list():
                    #     keyboard.add_button(button, VkKeyboardColor.PRIMARY)
                    # self.send_msg(event, message, keyboard)
            else:
                if not event.from_chat:
                    self.send_msg(event, 'Не понимаю...')

    def start_mode_start(self, event, message=''):
        self.polite = None
        keyboard = VkKeyboard(one_time=True)
        for button in self.menu.get_button_list():
            keyboard.add_button(button, VkKeyboardColor.PRIMARY)
        self.send_msg(event, f'{message} Текущий', keyboard)

    def start_mode_events(self, event):
        greetings = converter(self._BOT_CONFIG['greetings'])
        farewells = converter(self._BOT_CONFIG['farewells'])
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            self.print_message_description(event)
            text = event.text.lower()
            # Oтветы:
            if text in greetings and not self.menu.is_advanced:
                self.polite = 'greetings'
                keyboard = VkKeyboard(one_time=False)
                keyboard.add_button(self.menu.services['matchmaker']['button'],
                                    VkKeyboardColor.PRIMARY)
                greeting = greetings[randrange(len(greetings))]
                self.send_msg(event, f'{greeting.upper()},\n'
                                     f'{self.get_user_name(event.user_id)}!\n :))',
                              keyboard)
            elif text in farewells and not self.menu.is_advanced:
                self.polite = 'farewells'
                farewell = farewells[randrange(len(farewells))]
                self.send_msg(event, f'{farewell.upper()},\n'
                                     f'{self.get_user_name(event.user_id)}!\n :))')
            elif (text == self.menu.services['matchmaker']['command'].lower()
                  or text == self.menu.services['matchmaker']['button'].lower()):
                if event.from_chat:
                    self.polite = 'switching'
                    message = f'{self.get_user_name(event.user_id)}!\n'
                    self.send_msg(event, '{}Для продолжения переходи в чат с @{}!'.format(
                        message, self._BOT_CONFIG["name"]))
                self.menu.switch('matchmaker')
                self.matchmaker_mode_start(event, 'Спасибо за компанию,\n{}!'.format(
                    self.get_user_name(event.user_id)))
            else:
                if not event.from_chat:
                    self.send_msg(event, 'Не понимаю...')
        else:
            print(event.type)
            print()

    def send_msg(self, event, message, keyboard=None):
        """" Получает id пользователя ВК <user_id>, и сообщение ему """
        if event.from_chat:
            if self.polite:
                post = {'peer_id': event.peer_id, 'message': message, 'random_id': get_random_id()}
                self.send_msg_except(post)
                if self.polite != 'greetings':
                    message = None
        if message:
            post = {'peer_id': event.user_id, 'message': f'{message}{self.menu}', 'random_id': get_random_id()}
            if keyboard:
                post['keyboard'] = keyboard.get_keyboard()
            self.send_msg_except(post)

    def send_msg_except(self, post):
        try:
            self.vk_session.method('messages.send', post)
        except vk_api.exceptions.ApiError as no_permission:
            print(f'\t{no_permission}')

    def print_message_description(self, event):
        msg = 'Новое сообщение:\t'
        # msg += 'личное' if event.user_id > 0 else ''
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
