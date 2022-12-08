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


def split_str_to_list(string=' ', splitter=','):
    return list(c.strip() for c in string.strip().split(splitter))


class VkBot(Matchmaker):
    def __init__(self, bot: str = 'bot.cfg'):
        super(VkBot, self).__init__()
        self._BOT_CONFIG = get_bot_config(bot)
        self.menu = VkBotMenu(self._BOT_CONFIG['mode'])
        self.vk_session = vk_api.VkApi(token=self._BOT_CONFIG['token'])
        self.vk_api = self.vk_session.get_api()
        self.vk_tools = vk_api.VkTools(self.vk_session)
        print(f"Создан объект бота! (id={self.vk_session.app_id})")

    def get_group_users(self) -> list:
        return self.vk_tools.get_all('groups.getMembers', 1000, {'group_id': self._BOT_CONFIG['group_id']})['items']

    def get_keyboard(self, one_time=True) -> dict:
        keyboard = VkKeyboard(one_time)
        for button in self.menu.get_button_list():
            keyboard.add_button(button, VkKeyboardColor.PRIMARY)
        return keyboard.get_keyboard()

    def start(self):
        # Работа с сообщениями
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
                        self.search_mode_events(event)
                    else:
                        self.start_mode_events(event)
            except requests.exceptions.ReadTimeout as timeout:
                continue

    def search_mode_events(self, event):
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            self.print_message_description(event)
            text = event.text.lower()
            # Oтветы:
            if event.from_chat:
                self.send_msg_use_bot_dialog(event)
            elif self.exit(event):
                pass
            else:
                if not event.from_chat:
                    self.start_mode(event, 'Не понимаю...')

    def matchmaker_mode_events(self, event):
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            self.print_message_description(event)
            text = event.text.lower()
            # Oтветы:
            if event.from_chat:
                self.send_msg_use_bot_dialog(event)
            elif (text == self.menu.services['search']['command'].lower()
                  or text == self.menu.services['search']['button'].lower()):
                self.menu.switch('search')
                self.start_mode(event, '...Together forever,\n{}!'.format(self.get_user_name(event.user_id)))
            elif (text == self.menu.services['print']['command'].lower()
                  or text == self.menu.services['print']['button'].lower()):
                self.start_mode(event, 'Ok,\n{}!'.format(self.get_user_name(event.user_id)))
            elif self.exit(event):
                pass
            else:
                if not event.from_chat:
                    self.start_mode(event, 'Не понимаю...')

    def start_mode_events(self, event):
        greetings = split_str_to_list(self._BOT_CONFIG['greetings'])
        farewells = split_str_to_list(self._BOT_CONFIG['farewells'])
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            self.print_message_description(event)
            text = event.text.lower()
            # Oтветы:
            if text in greetings:
                greeting = greetings[randrange(len(greetings))]
                message = '{},\n{}!\n :))'.format(greeting.upper(), self.get_user_name(event.user_id))
                self.start_mode(event, message)
            elif text in farewells:
                farewell = farewells[randrange(len(farewells))]
                self.send_msg(event.peer_id, f'{farewell.upper()},\n{self.get_user_name(event.user_id)}!\n :))')
            elif (text == self.menu.services['matchmaker']['command'].lower()
                  or text == self.menu.services['matchmaker']['button'].lower()):
                self.menu.switch('matchmaker')
                self.start_mode(event, 'Спасибо за компанию,\n{}!'.format(self.get_user_name(event.user_id)))
                self.send_msg_use_bot_dialog(event)
            else:
                self.start_mode(event, 'Не понимаю...')
        else:
            print(event.type)
            print()

    def start_mode(self, event, message=''):
        post = {'peer_id': event.peer_id, 'random_id': get_random_id(),
                'message': message if event.from_chat else f'{message} Текущий{self.menu}'}
        if not event.from_chat:
            post['keyboard'] = self.get_keyboard()
        self.send_post(post)

    def exit(self, event) -> bool:
        text = event.text.lower()
        if (text == self.menu.services['exit']['command'].lower()
                or text == self.menu.services['exit']['button'].lower()):
            message = '{},\nсервис "{}" закрыт!'.format(self.get_user_name(event.user_id), self.menu.button)
            self.menu.exit()
            self.start_mode(event, message)
            return True
        return False

    def send_msg(self, peer_id, message, keyboard=None):
        """" Получает id пользователя ВК <user_id>, и сообщение ему """
        post = {'peer_id': peer_id, 'random_id': get_random_id(), 'message': message}
        if keyboard:
            post['keyboard'] = keyboard.get_keyboard()
        self.send_post(post)

    def send_post(self, post):
        try:
            self.vk_session.method('messages.send', post)
        except vk_api.exceptions.ApiError as no_permission:
            print(f'\t{no_permission}')

    def send_msg_use_bot_dialog(self, event):
        if not event.from_user:
            self.send_msg(event.peer_id, '{} Юзать сервис переходи в чат с @{}!'.format(
                f'{self.get_user_name(event.user_id)}!\n', self._BOT_CONFIG["name"]))

    def print_message_description(self, event):
        msg = 'Новое сообщение:\t'
        msg += f'из чата {event.chat_id}' if event.from_chat else ''
        msg += f'\nот: {self.get_user_title(event.user_id)})'
        msg += f' *--- {event.text}'
        print(msg)
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
