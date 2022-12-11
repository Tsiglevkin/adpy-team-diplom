#

from random import randrange
from pprint import pprint

import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.bot_longpoll import VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from bot_config.config import get_config
from vk_tools.vk_bot_menu import VkBotMenu
from vk_tools.matchmaker import Matchmaker


def split_str_to_list(string=' ', splitter=','):
    return list(c.strip() for c in string.strip().split(splitter))


class VkBot(Matchmaker):
    def __init__(self, bot='bot.cfg'):
        super(VkBot, self).__init__()
        self._BOT_CONFIG: dict = get_config()
        self.group_id = self._BOT_CONFIG['group_id']
        self.menu = VkBotMenu()
        self.vk_session = vk_api.VkApi(token=self._BOT_CONFIG['token'])
        self.vk_tools = vk_api.VkTools(self.vk_session)
        self.vk_api = self.vk_session.get_api()
        print(f"Создан объект бота! (id={self.vk_session.app_id})")

    def get_keyboard(self, one_time=True) -> dict:
        keyboard = VkKeyboard(one_time)
        buttons = self.menu.get_buttons()
        buttons_peer_line = 0
        for num, button in enumerate(buttons['buttons']):
            if num and buttons['max'] and num % buttons['max'] == 0:
                keyboard.add_line()
                buttons_peer_line = 0
            else:
                buttons_peer_line += 1
            if buttons_peer_line < 4:
                keyboard.add_button(button, VkKeyboardColor.PRIMARY)
            else:
                print('Слишком много кнопок для одной строки!')
                break
        return keyboard.get_keyboard()

    def start(self):
        # Работа с сообщениями
        greetings = split_str_to_list(self._BOT_CONFIG['greetings'])
        farewells = split_str_to_list(self._BOT_CONFIG['farewells'])
        while True:
            longpoll = VkLongPoll(self.vk_session, group_id=self.group_id)
            print('Запущен бот группы id =', longpoll.group_id)
            try:
                for event in longpoll.listen():
                    if self.menu.service_name == 'start-up':
                        self.start_mode_events(event)
                    elif self.menu.service_name == 'matchmaker':
                        self.matchmaker_mode_events(event)
                    elif self.menu.service_name == 'search':
                        self.search_mode_events(event)
                    elif self.menu.service_name == 'filter':
                        self.search_filter_mode_events(event)
                    elif self.menu.service_name == 'standard':
                        self.search_standard_filter_mode_events(event)
                    elif self.menu.service_name == 'advisable':
                        self.search_advisable_mode_events(event)
                    else:
                        self.start_mode_events(event)
            except requests.exceptions.ReadTimeout as timeout:
                continue

    def search_standard_filter_mode_events(self, event):
        menu = self.menu.services
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            self.print_message_description(event)
            text = event.text.lower()
            # Oтветы:
            try:
                if event.from_chat:
                    self.send_msg_use_bot_dialog(event)
                elif text == menu['male']['command'].lower() or text == menu['male']['button'].lower():
                    self.start_mode(event, 'Ok,\n{}!'.format(self.get_user_name(event.user_id)))
                elif text == menu['female']['command'].lower() or text == menu['female']['button'].lower():
                    self.start_mode(event, 'Ok,\n{}!'.format(self.get_user_name(event.user_id)))
                elif text == menu['any gender']['command'].lower() or text == menu['any gender']['button'].lower():
                    self.start_mode(event, 'Ok,\n{}!'.format(self.get_user_name(event.user_id)))
                elif text == menu['younger']['command'].lower() or text == menu['younger']['button'].lower():
                    self.start_mode(event, 'Ok,\n{}!'.format(self.get_user_name(event.user_id)))
                elif text == menu['older']['command'].lower() or text == menu['older']['button'].lower():
                    self.start_mode(event, 'Ok,\n{}!'.format(self.get_user_name(event.user_id)))
                elif text == menu['any gage']['command'].lower() or text == menu['any age']['button'].lower():
                    self.start_mode(event, 'Ok,\n{}!'.format(self.get_user_name(event.user_id)))
                elif text == menu['city']['command'].lower() or text == menu['city']['button'].lower():
                    self.start_mode(event, 'Ok,\n{}!'.format(self.get_user_name(event.user_id)))
                elif text == menu['any city']['command'].lower() or text == menu['any city']['button'].lower():
                    self.start_mode(event, 'Ok,\n{}!'.format(self.get_user_name(event.user_id)))
                elif self.exit(event):
                    pass
                else:
                    if not event.from_chat:
                        self.start_mode(event, 'Не понимаю...')
            except KeyError as key_err:
                self.my_except(event, key_err, f'Попытка взять значение по ошибочному ключу {key_err} для', menu)
            except Exception as other:
                self.my_except(event, other)

    def my_except(self, event, err, msg='', menu=None):
        if msg:
            print(msg)
        print(err)
        if menu:
            pprint(menu)
        self.exit(event)

    def search_filter_mode_events(self, event):
        menu = self.menu.services
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            self.print_message_description(event)
            text = event.text.lower()
            # Oтветы:
            try:
                if event.from_chat:
                    self.send_msg_use_bot_dialog(event)
                elif text == menu['standard']['command'].lower() or text == menu['standard']['button'].lower():
                    self.menu.switch('standard')
                    self.start_mode(event, 'Ok,\n{}!'.format(self.get_user_name(event.user_id)))
                elif text == menu['interests']['command'].lower() or text == menu['interests']['button'].lower():
                    self.start_mode(event, 'Ok,\n{}!'.format(self.get_user_name(event.user_id)))
                elif text == menu['advanced']['command'].lower() or text == menu['advanced']['button'].lower():
                    self.start_mode(event, 'Ok,\n{}!'.format(self.get_user_name(event.user_id)))
                elif self.exit(event):
                    pass
                else:
                    if not event.from_chat:
                        self.start_mode(event, 'Не понимаю...')
            except KeyError as key_err:
                self.my_except(event, key_err, f'Попытка взять значение по ошибочному ключу {key_err} для', menu)
            except Exception as other:
                self.my_except(event, other)

    def search_advisable_mode_events(self, event, search_filter_json_file: str = 'search_filter'):
        menu = self.menu.services
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            self.print_message_description(event)
            text = event.text.lower()
            # Oтветы:
            try:
                if event.from_chat:
                    self.send_msg_use_bot_dialog(event)
                elif text == menu['next']['command'].lower() or text == menu['next']['button'].lower():
                    self.start_mode(event, 'Ok,\n{}!'.format(self.get_user_name(event.user_id)))
                elif text == menu['save']['command'].lower() or text == menu['save']['button'].lower():
                    self.start_mode(event, 'Ok,\n{}!'.format(self.get_user_name(event.user_id)))
                elif self.exit(event):
                    pass
                else:
                    if not event.from_chat:
                        self.start_mode(event, 'Не понимаю...')
            except KeyError as key_err:
                self.my_except(event, key_err, f'Попытка взять значение по ошибочному ключу {key_err} для', menu)
            except Exception as other:
                self.my_except(event, other)

    def search_mode_events(self, event):
        menu = self.menu.services
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            self.print_message_description(event)
            text = event.text.lower()
            # Oтветы:
            try:
                if event.from_chat:
                    self.send_msg_use_bot_dialog(event)
                elif text == menu['filter']['command'].lower() or text == menu['filter']['button'].lower():
                    self.menu.switch('filter')
                    self.start_mode(event, '...And hello again,\n{}!'.format(self.get_user_name(event.user_id)))
                elif text == menu['advisable']['command'].lower() or text == menu['advisable']['button'].lower():
                    self.menu.switch('advisable')
                    self.start_mode(event, '...And hello again,\n{}!'.format(self.get_user_name(event.user_id)))
                    self.search_advisable_users(self.group_id, self.vk_tools)
                elif self.exit(event):
                    pass
                else:
                    if not event.from_chat:
                        self.start_mode(event, 'Не понимаю...')
            except KeyError as key_err:
                self.my_except(event, key_err, f'Попытка взять значение по ошибочному ключу {key_err} для', menu)
            except Exception as other:
                self.my_except(event, other)

    def matchmaker_mode_events(self, event):
        menu = self.menu.services
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            self.print_message_description(event)
            text = event.text.lower()
            # Oтветы:
            try:
                if event.from_chat:
                    self.send_msg_use_bot_dialog(event)
                elif text == menu['search']['command'].lower() or text == menu['search']['button'].lower():
                    self.menu.switch('search')
                    self.start_mode(event, '...Together forever,\n{}!'.format(self.get_user_name(event.user_id)))
                    # self.refresh_group_users(self.group_id, self.vk_tools)
                elif text == menu['print']['command'].lower() or text == menu['print']['button'].lower():
                    self.start_mode(event, 'Ok,\n{}!'.format(self.get_user_name(event.user_id)))
                elif self.exit(event):
                    pass
                else:
                    if not event.from_chat:
                        self.start_mode(event, 'Не понимаю...')
            except KeyError as key_err:
                self.my_except(event, key_err, f'Попытка взять значение по ошибочному ключу {key_err} для', menu)
            except Exception as other:
                self.my_except(event, other)

    def start_mode_events(self, event):
        menu = self.menu.services
        greetings = split_str_to_list(self._BOT_CONFIG['greetings'])
        farewells = split_str_to_list(self._BOT_CONFIG['farewells'])
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            self.print_message_description(event)
            text = event.text.lower()
            # Oтветы:
            try:
                if text in greetings:
                    greeting = greetings[randrange(len(greetings))]
                    message = '{},\n{}!\n :))'.format(greeting.upper(), self.get_user_name(event.user_id))
                    self.start_mode(event, message)
                elif text in farewells:
                    farewell = farewells[randrange(len(farewells))]
                    self.send_msg(event.peer_id, f'{farewell.upper()},\n{self.get_user_name(event.user_id)}!\n :))')
                elif text == menu['matchmaker']['command'].lower() or text == menu['matchmaker']['button'].lower():
                    self.menu.switch('matchmaker')
                    self.start_mode(event, 'Спасибо за компанию,\n{}!'.format(self.get_user_name(event.user_id)))
                    self.send_msg_use_bot_dialog(event)
                else:
                    self.start_mode(event, 'Не понимаю...')
            except KeyError as key_err:
                self.my_except(event, key_err, f'Попытка взять значение по ошибочному ключу {key_err} для', menu)
            except Exception as other:
                self.my_except(event, other)
        else:
            print(event.type)
            print()

    def start_mode(self, event, message=''):
        post = {'peer_id': event.peer_id, 'random_id': get_random_id(),
                'message': message if event.from_chat else f'{message} Текущий{self.menu}'}
        if not event.from_chat:
            post['keyboard'] = self.get_keyboard()
        self.send_post(post)
        return post

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
        return post

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
        # msg += 'личное' if event.user_id > 0 else ''
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
