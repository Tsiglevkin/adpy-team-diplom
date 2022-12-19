#

from random import randrange
from pprint import pprint

import requests
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType, VkBotMessageEvent
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from bot_config.config import get_config
from vk_tools.vk_bot_menu import VkBotMenu
from vk_tools.standard_checker import StandardChecker, get_standard_filter


def split_str_to_list(string=' ', splitter=','):
    return list(c.strip() for c in string.strip().split(splitter))


def filter_switch(switch_filter, filter_2):
    if switch_filter['filter'] and filter_2['filter']:
        switch_filter['filter'] = ''
        filter_2['filter'] = ''
    if not switch_filter['filter'] and filter_2['filter']:
        filter_2['filter'] = ''
    else:
        switch_filter['filter'] = not switch_filter['filter']


def filter_switch_2(switch_filter, filter_2, filter_3):
    if switch_filter['filter'] and filter_2['filter'] and filter_3['filter']:
        switch_filter['filter'] = ''
        filter_2['filter'] = ''
        filter_3['filter'] = ''
    if not switch_filter['filter'] and filter_2['filter'] and filter_3['filter']:
        filter_2['filter'] = ''
        filter_3['filter'] = ''
    else:
        switch_filter['filter'] = not switch_filter['filter']


class VkBot:
    # виды callback-кнопок
    __callback_types__ = ("show_snackbar", "open_link", "open_app")

    def __init__(self, bot='bot.cfg'):
        self._BOT_CONFIG: dict = get_config()
        self.group_id = self._BOT_CONFIG['group_id']
        self.menu = VkBotMenu()
        self.vk_session = vk_api.VkApi(token=self._BOT_CONFIG['token'])  # vk_api.vk_api.VkApi
        self.longpoll = VkBotLongPoll(self.vk_session, group_id=self.group_id)
        self.event: VkBotMessageEvent = None
        self.vk_tools = vk_api.VkTools(self.vk_session)  # vk_api.tools.VkTools
        self.vk_api_methods = self.vk_session.get_api()  # vk_api.vk_api.VkApiMethod
        print(f"Создан объект бота! (id={self.vk_session.app_id})")

    def get_keyboard(self, callback=False, inline=False, one_time=False, empty=False) -> dict:
        keyboard = VkKeyboard(inline=inline, one_time=False if inline else one_time)
        if empty:
            return keyboard.get_empty_keyboard()
        buttons = self.menu.get_buttons()
        buttons_peer_line = 0
        for num, button in enumerate(buttons['buttons']):
            if num and buttons['max'] and num % buttons['max'] == 0:
                keyboard.add_line()
                buttons_peer_line = 0
            else:
                buttons_peer_line += 1
            if buttons_peer_line < 4:
                if callback:
                    keyboard.add_callback_button(
                        label=button,
                        color=VkKeyboardColor.NEGATIVE if buttons['filter'][num] else VkKeyboardColor.PRIMARY,
                        payload={"type": "show_snackbar", "text": "Это исчезающее сообщение на экране"}, )
                else:
                    keyboard.add_button(
                        button, VkKeyboardColor.NEGATIVE if buttons['filter'][num] else VkKeyboardColor.PRIMARY)
            else:
                print('Слишком много кнопок для одной строки!')
                break
        return keyboard.get_keyboard()

    def start(self):
        # Работа с сообщениями
        while True:
            print('Запущен бот группы id =', self.longpoll.group_id)
            try:
                for event in self.longpoll.listen():
                    self.event = event
                    if self.menu.service_name == 'start-up':
                        self.start_mode_events()
                    elif self.menu.service_name == 'matchmaker':
                        self.matchmaker_mode_events()
                    elif self.menu.service_name == 'search':
                        self.search_mode_events()
                    elif self.menu.service_name == 'filter':
                        self.search_filter_mode_events()
                    elif self.menu.service_name == 'standard':
                        self.search_standard_filter_mode_events()
                    elif self.menu.service_name == 'advisable':
                        self.search_advisable_mode_events()
                    else:
                        self.start_mode_events()
            except requests.exceptions.ReadTimeout as timeout:
                continue

    def search_standard_filter_mode_events(self):
        menu = self.menu.services
        if self.event.type == VkBotEventType.MESSAGE_NEW:
            self.print_message_description()
            text = self.event.message['text'].lower()
            # Oтветы:
            try:
                if self.event.from_chat:
                    self.send_msg_use_bot_dialog()
                elif text == menu['male']['command'].lower() or text == menu['male']['button'].lower():
                    filter_switch(menu['male'], menu['female'])
                    self.start_mode(message='Ok,\n{}!'.format(self.get_user_name()))
                elif text == menu['female']['command'].lower() or text == menu['female']['button'].lower():
                    filter_switch(menu['female'], menu['male'])
                    self.start_mode(message='Ok,\n{}!'.format(self.get_user_name()))
                elif text == menu['city']['command'].lower() or text == menu['city']['button'].lower():
                    menu['city']['filter'] = not menu['city']['filter']
                    self.start_mode(message='Ok,\n{}!'.format(self.get_user_name()))
                elif text == menu['younger']['command'].lower() or text == menu['younger']['button'].lower():
                    filter_switch_2(menu['younger'], menu['older'], menu['peers'])
                    self.start_mode(message='Ok,\n{}!'.format(self.get_user_name()))
                elif text == menu['older']['command'].lower() or text == menu['older']['button'].lower():
                    filter_switch_2(menu['older'], menu['younger'], menu['peers'])
                    self.start_mode(message='Ok,\n{}!'.format(self.get_user_name()))
                elif text == menu['peers']['command'].lower() or text == menu['peers']['button'].lower():
                    filter_switch_2(menu['peers'], menu['older'], menu['younger'])
                    self.start_mode(message='Ok,\n{}!'.format(self.get_user_name()))
                elif self.exit():
                    pass
                else:
                    if not self.event.from_chat:
                        self.start_mode(message='Не понимаю...')
                msg = self.send_filter(message='Настроен Фильтр для поиска\t'
                                       )['message'] if self.menu.get_filter_string() else ''
            except KeyError as key_err:
                self.my_except(key_err, f'Попытка взять значение по ошибочному ключу {key_err}'
                                        f' в search_standard_filter_mode_events', menu)
                # raise key_err
            except Exception as other:
                self.my_except(other)
                # raise other

    def my_except(self, err: Exception = None, msg='', menu: dict = None):
        if msg:
            print(msg)
        print(err)
        if menu:
            pprint(menu)
        self.exit()

    def search_filter_mode_events(self):
        menu = self.menu.services
        if self.event.type == VkBotEventType.MESSAGE_NEW:
            self.print_message_description()
            text = self.event.message['text'].lower()
            # Oтветы:
            try:
                if self.event.from_chat:
                    self.send_msg_use_bot_dialog()
                elif text == menu['standard']['command'].lower() or text == menu['standard']['button'].lower():
                    self.menu.switch('standard')
                    self.start_mode(message='Ok,\n{}!'.format(self.get_user_name()))
                elif text == menu['interests']['command'].lower() or text == menu['interests']['button'].lower():
                    self.start_mode(message='Модуль в разработке,\n{}!'.format(self.get_user_name()))
                elif text == menu['advanced']['command'].lower() or text == menu['advanced']['button'].lower():
                    self.start_mode(message='Модуль в разработке,\n{}!'.format(self.get_user_name()))
                elif self.exit():
                    std_filter = get_standard_filter(menu)['buttons']
                    print('{}:\t{}'.format(self.menu.button,
                                           std_filter if std_filter else 'Стандартный фильтр не задан...'))
                else:
                    if not self.event.from_chat:
                        self.start_mode(message='Не понимаю...')
            except KeyError as key_err:
                self.my_except(key_err, f'Попытка взять значение по ошибочному-1 ключу {key_err}', menu)
            except Exception as other:
                self.my_except(other)
                raise other

    def search_mode_events(self):
        menu = self.menu.services
        self.menu.get_filter_string()
        if self.event.type == VkBotEventType.MESSAGE_NEW:
            self.print_message_description()
            text = self.event.message['text'].lower()
            # Oтветы:
            try:
                if self.event.from_chat:
                    self.send_msg_use_bot_dialog()
                elif text == menu['filter']['command'].lower() or text == menu['filter']['button'].lower():
                    self.menu.switch('filter')
                    self.start_mode(message='...And hello again,\n{}!'.format(self.get_user_name()))
                elif text == menu['advisable']['command'].lower() or text == menu['advisable']['button'].lower():
                    search_filter = menu['filter']['services']
                    std_filter = get_standard_filter(search_filter)['buttons']
                    self.menu.switch('advisable')
                    self.start_mode(clear_keyboard=True,
                                    message='...And hello again,\n{}!\nИщем по фильтрам\n{}.\t'.format(
                                        self.get_user_name(),
                                        std_filter if std_filter else 'Стандартный фильтр не задан...'))
                    self.send_msg(message='Терпение! Идёт поиск подходящих пиплов...',
                                  attachment='doc49903553_642595119')
                    self.search_advisable_users(client_id=self.event.message['from_id'], search_filter=search_filter)
                elif self.exit():
                    pass
                else:
                    if not self.event.from_chat:
                        self.start_mode(message='Не понимаю...')
            except KeyError as key_err:
                self.my_except(key_err, f'Попытка взять значение по ошибочному-2 ключу {key_err}', menu)
            except Exception as other:
                self.my_except(other)
                raise other

    def search_advisable_users(self, client_id, search_filter):
        print('Модуль в разработке!')

    def search_advisable_mode_events(self):
        print('Модуль в разработке!')

    def matchmaker_mode_events(self):
        menu = self.menu.services
        if self.event.type == VkBotEventType.MESSAGE_NEW:
            self.print_message_description()
            text = self.event.message['text'].lower()
            # Oтветы:
            try:
                if self.event.from_chat:
                    self.send_msg_use_bot_dialog()
                elif text == menu['search']['command'].lower() or text == menu['search']['button'].lower():
                    self.menu.switch('search')
                    self.start_mode(message='...Together forever,\n{}!'.format(self.get_user_name()))
                elif text == menu['print']['command'].lower() or text == menu['print']['button'].lower():
                    self.start_mode(message='Модуль в разработке,\n{}!'.format(self.get_user_name()))
                elif self.exit():
                    pass
                else:
                    if not self.event.from_chat:
                        self.start_mode(message='Не понимаю...')
            except KeyError as key_err:
                self.my_except(key_err, f'Попытка взять значение по ошибочному ключу {key_err}'
                                        f' в matchmaker_mode_events', menu)
                # raise key_err
            except Exception as other:
                self.my_except(other)
                # raise other

    def start_mode_events(self):
        menu = self.menu.services
        greetings = split_str_to_list(self._BOT_CONFIG['greetings'])
        farewells = split_str_to_list(self._BOT_CONFIG['farewells'])
        # if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        if self.event.type == VkBotEventType.MESSAGE_NEW:
            self.print_message_description()
            # text = event.text.lower()
            text = self.event.message['text'].lower()
            # Oтветы:
            if text:
                if self.event.from_user:
                    # Если клиент пользователя не поддерживает callback-кнопки, нажатие на них будет
                    # отправлять  текстовые сообщения. Т.е. они будут работать как обычные inline кнопки.
                    if "callback" not in self.event.obj.client_info["button_actions"]:
                        print(f'Клиент user_id{self.event.obj.message["from_id"]} не поддерживает callback-кнопки.')
                try:
                    if text in greetings:
                        greeting = greetings[randrange(len(greetings))]
                        message = '{},\n{}!\n :))'.format(greeting.upper(), self.get_user_name())
                        self.start_mode(message=message, inline=True)
                    elif text in farewells:
                        farewell = farewells[randrange(len(farewells))]
                        self.send_msg(message=f'{farewell.upper()},\n{self.get_user_name()}!\n :))')
                    elif text == menu['matchmaker']['command'].lower() or text == menu['matchmaker']['button'].lower():
                        self.menu.switch('matchmaker')
                        self.start_mode(message='Спасибо за компанию,\n{}!'.format(self.get_user_name()))
                        self.send_msg_use_bot_dialog()
                    else:
                        self.start_mode(message='Не понимаю...', inline=True)
                except KeyError as key_err:
                    self.my_except(key_err, f'Попытка взять значение по ошибочному ключу {key_err}'
                                            f' в start_mode_events', menu)
                    # raise key_err
                except Exception as other:
                    self.my_except(other)
                    # raise other

        elif self.event.type == VkBotEventType.MESSAGE_REPLY:
            print('\nНовое сообщение:')
            print('От меня для: ', end='')
            print(self.event.obj.peer_id)
            print('Текст:\n', self.event.obj.text.lower())
            print()

        elif self.event.type == VkBotEventType.MESSAGE_TYPING_STATE:
            print('\nПечатает ', end='')
            print(self.event.message['from_id'], end=' ')
            print('для ', end='')
            print(self.event.message['to_id'])
            print()

        elif self.event.type == VkBotEventType.GROUP_JOIN:
            print('\n', self.event.message['from_id'], end=' ')
            print('Вступил в группу!')
            print()

        elif self.event.type == VkBotEventType.GROUP_LEAVE:
            print('\n', self.event.message['from_id'], end=' ')
            print('Покинул группу!')
            print()

        elif self.event.type == VkBotEventType.MESSAGE_EVENT:
            # Callback кнопки не срабатывают: события не происходит ???
            print(self.event.type)
            print()

        else:
            print(self.event.type)
            print()

    def start_mode(self, peer_id='', message='', inline=False, callback=False, clear_keyboard=False):
        if not peer_id:
            peer_id = self.event.message["peer_id"]
        post = {'peer_id': peer_id, 'random_id': get_random_id(),
                'message': message if self.event.from_chat else f'{message} Текущий{self.menu}'}
        if not self.event.from_chat:
            post['keyboard'] = self.get_keyboard(inline=inline, callback=callback, empty=clear_keyboard)
        self.send_post(post)
        return post

    def exit(self, callback=False) -> bool:
        menu = self.menu.services
        # text = event.text.lower()
        text = self.event.message['text'].lower()
        if text == menu['exit']['button'].lower() or text == menu['exit']['command'].lower():
            message = '{},\nсервис "{}" закрыт!'.format(self.get_user_name(), self.menu.button)
            self.menu.exit()
            self.start_mode(message=message, callback=callback)
            return True
        return False

    def send_filter(self, message=''):
        """" Сообщение пользователю о выбранных фильтрах стандартного поиска подходящих пиплов """
        std_filter = self.menu.get_filter_string()
        message += '\n{}:\t{}'.format(self.menu.button, std_filter if std_filter else 'фильтр не задан...')
        post = {'peer_id': self.event.message["peer_id"], 'random_id': get_random_id(), 'message': message,
                'keyboard': self.get_keyboard()}
        self.send_post(post)
        print(message)
        return post

    def send_msg(self, peer_id='', message='', keyboard=None, attachment=''):
        """" Получает id пользователя ВК <user_id>, и сообщение ему """
        if not peer_id:
            peer_id = self.event.message["peer_id"]
        post = {'peer_id': peer_id, 'random_id': get_random_id(), 'message': message, 'attachment': attachment}
        if keyboard:
            post['keyboard'] = keyboard  # .get_keyboard()
        self.send_post(post)
        return post

    def send_post(self, post):
        try:
            self.vk_session.method('messages.send', post)
        except vk_api.exceptions.ApiError as no_permission:
            print(f'\t{no_permission}')

    def send_msg_use_bot_dialog(self):
        if not self.event.from_user:
            self.send_msg(message='{} Юзать сервис переходи в чат с @{}!'.format(
                f'{self.get_user_name()}!\n', self._BOT_CONFIG["name"]))

    def print_message_description(self):
        msg = f'\nНовое сообщение\t{self.event.t}:'
        msg += f'из чата {self.event.chat_id}' if self.event.from_chat else ''
        msg += f'\nот: {self.get_user_title()}'
        msg += f' *--- {self.event.message["text"]}'
        print(msg)
        # print('*---', event.from_user, event.from_chat, event.from_group, event.from_me)
        return msg

    def get_user(self, user_id='', name_case='nom', fields="city"):
        """ Получаем пользователя """
        if not user_id:
            user_id = self.event.message["from_id"]
        return self.vk_api_methods.users.get(user_ids=user_id, fields=fields, name_case=name_case)[0]

    def get_user_name(self, user_id='', name_case='nom'):
        """ Получаем имя пользователя"""
        if not user_id:
            user_id = self.event.message["from_id"]
        user = self.get_user(user_id=user_id, name_case=name_case)
        return f'{user.get("first_name", "")} {user.get("last_name", "")}'

    def get_user_city(self, user_id=''):
        if not user_id:
            user_id = self.event.message["from_id"]
        user = self.get_user(user_id=user_id)
        return user.get("city", '')

    def get_user_title(self, user_id=''):
        """ Получаем кратко пользователя"""
        if not user_id:
            user_id = self.event.message["from_id"]
        user = self.get_user(user_id=user_id, name_case='gen')
        return f'{user.get("last_name", "")} {user.get("first_name", "")} (id = {user_id})'
