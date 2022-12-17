#

import json
from random import randrange
from pprint import pprint

import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from bot_config.config import get_config
from vk_tools.vk_bot_menu import VkBotMenu
# from vk_tools.matchmaker import Matchmaker
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
        self.vk_tools = vk_api.VkTools(self.vk_session)   # vk_api.tools.VkTools
        self.vk_api_methods = self.vk_session.get_api()  # vk_api.vk_api.VkApiMethod
        print(f"Создан объект бота! (id={self.vk_session.app_id})")

    def get_keyboard(self, callback=False, inline=False, one_time=False) -> dict:
        menu = self.menu.services
        keyboard = VkKeyboard(inline=inline, one_time=False if inline else one_time)
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
        # print()
        # pprint(self.__dict__)   # -----------------
        # Работа с сообщениями
        while True:
            longpoll = VkBotLongPoll(self.vk_session, group_id=self.group_id)
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
        if event.type == VkBotEventType.MESSAGE_NEW:
            self.print_message_description(event)
            text = event.message['text'].lower()
            # Oтветы:
            try:
                if event.from_chat:
                    self.send_msg_use_bot_dialog(event)
                elif text == menu['male']['command'].lower() or text == menu['male']['button'].lower():
                    filter_switch(menu['male'], menu['female'])
                    self.start_mode(event, 'Ok,\n{}!'.format(self.get_user_name(event)))
                elif text == menu['female']['command'].lower() or text == menu['female']['button'].lower():
                    filter_switch(menu['female'], menu['male'])
                    self.start_mode(event, 'Ok,\n{}!'.format(self.get_user_name(event)))
                elif text == menu['city']['command'].lower() or text == menu['city']['button'].lower():
                    menu['city']['filter'] = not menu['city']['filter']
                    self.start_mode(event, 'Ok,\n{}!'.format(self.get_user_name(event)))
                elif text == menu['younger']['command'].lower() or text == menu['younger']['button'].lower():
                    filter_switch_2(menu['younger'], menu['older'], menu['peers'])
                    self.start_mode(event, 'Ok,\n{}!'.format(self.get_user_name(event)))
                elif text == menu['older']['command'].lower() or text == menu['older']['button'].lower():
                    filter_switch_2(menu['older'], menu['younger'], menu['peers'])
                    self.start_mode(event, 'Ok,\n{}!'.format(self.get_user_name(event)))
                elif text == menu['peers']['command'].lower() or text == menu['peers']['button'].lower():
                    filter_switch_2(menu['peers'], menu['older'], menu['younger'])
                    self.start_mode(event, 'Ok,\n{}!'.format(self.get_user_name(event)))
                elif self.exit(event):
                    pass
                else:
                    if not event.from_chat:
                        self.start_mode(event, 'Не понимаю...')
                msg = self.send_filter(event, 'Настроен Фильтр для поиска\t'
                                       )['message'] if self.menu.get_filter_string() else ''
            except KeyError as key_err:
                self.my_except(event, key_err, f'Попытка взять значение по ошибочному ключу {key_err}'
                                               f' в search_standard_filter_mode_events(self, event)', menu)
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
        if event.type == VkBotEventType.MESSAGE_NEW:
            self.print_message_description(event)
            text = event.message['text'].lower()
            # Oтветы:
            try:
                if event.from_chat:
                    self.send_msg_use_bot_dialog(event)
                elif text == menu['standard']['command'].lower() or text == menu['standard']['button'].lower():
                    self.menu.switch('standard')
                    self.start_mode(event, 'Ok,\n{}!'.format(self.get_user_name(event)))
                elif text == menu['interests']['command'].lower() or text == menu['interests']['button'].lower():
                    self.start_mode(event, 'Модуль в разработке,\n{}!'.format(self.get_user_name(event)))
                elif text == menu['advanced']['command'].lower() or text == menu['advanced']['button'].lower():
                    self.start_mode(event, 'Модуль в разработке,\n{}!'.format(self.get_user_name(event)))
                elif self.exit(event):
                    std_filter = get_standard_filter(menu)['buttons']
                    print('{}:\t{}'.format(self.menu.button,
                                           std_filter if std_filter else 'Стандартный фильтр не задан...'))
                else:
                    if not event.from_chat:
                        self.start_mode(event, 'Не понимаю...')
            except KeyError as key_err:
                self.my_except(event, key_err, f'Попытка взять значение по ошибочному-1 ключу {key_err}', menu)
            except Exception as other:
                self.my_except(event, other)

    def search_advisable_mode_events(self, event):
        menu = self.menu.services
        if event.type == VkBotEventType.MESSAGE_NEW:
            self.print_message_description(event)
            text = event.message['text'].lower()
            # Oтветы:
            try:
                if event.from_chat:
                    self.send_msg_use_bot_dialog(event)
                elif text == menu['next']['command'].lower() or text == menu['next']['button'].lower():
                    self.start_mode(event, 'Ok,\n{}!'.format(self.get_user_name(event)))
                elif text == menu['save']['command'].lower() or text == menu['save']['button'].lower():
                    self.start_mode(event, 'Ok,\n{}!'.format(self.get_user_name(event)))
                elif self.exit(event):
                    pass
                else:
                    if not event.from_chat:
                        self.start_mode(event, 'Не понимаю...')
            except KeyError as key_err:
                self.my_except(event, key_err, f'Попытка взять значение по ошибочному ключу {key_err}', menu)
            except Exception as other:
                self.my_except(event, other)

    def search_mode_events(self, event):
        menu = self.menu.services
        self.menu.get_filter_string()
        if event.type == VkBotEventType.MESSAGE_NEW:
            self.print_message_description(event)
            text = event.message['text'].lower()
            # Oтветы:
            try:
                if event.from_chat:
                    self.send_msg_use_bot_dialog(event)
                elif text == menu['filter']['command'].lower() or text == menu['filter']['button'].lower():
                    self.menu.switch('filter')
                    self.start_mode(event, '...And hello again,\n{}!'.format(self.get_user_name(event)))
                elif text == menu['advisable']['command'].lower() or text == menu['advisable']['button'].lower():
                    search_filter = menu['filter']['services']
                    std_filter = get_standard_filter(search_filter)['buttons']
                    self.menu.switch('advisable')
                    self.start_mode(event=event,
                                    message='...And hello again,\n{}!\nИщем по фильтрам\n{}.\t'.format(
                                        self.get_user_name(event),
                                        std_filter if std_filter else 'Стандартный фильтр не задан...'))

                    self.search_advisable_users(client_id=event.message['from_id'], search_filter=search_filter)
                elif self.exit(event):
                    pass
                else:
                    if not event.from_chat:
                        self.start_mode(event, 'Не понимаю...')
            except KeyError as key_err:
                self.my_except(event, key_err, f'Попытка взять значение по ошибочному-2 ключу {key_err}', menu)
            except Exception as other:
                self.my_except(event, other)

    def search_advisable_users(self, client_id, search_filter):
        print('Модуль в разработке')

    def matchmaker_mode_events(self, event):
        menu = self.menu.services
        if event.type == VkBotEventType.MESSAGE_NEW:
            self.print_message_description(event)
            text = event.message['text'].lower()
            # Oтветы:
            try:
                if event.from_chat:
                    self.send_msg_use_bot_dialog(event)
                elif text == menu['search']['command'].lower() or text == menu['search']['button'].lower():
                    self.menu.switch('search')
                    self.start_mode(event, '...Together forever,\n{}!'.format(self.get_user_name(event)))
                    # self.refresh_group_users(self.group_id, self.vk_tools)
                elif text == menu['print']['command'].lower() or text == menu['print']['button'].lower():
                    self.start_mode(event, 'Модуль в разработке,\n{}!'.format(self.get_user_name(event)))
                elif self.exit(event):
                    pass
                else:
                    if not event.from_chat:
                        self.start_mode(event, 'Не понимаю...')
            except KeyError as key_err:
                self.my_except(event, key_err, f'Попытка взять значение по ошибочному ключу {key_err}', menu)
            except Exception as other:
                self.my_except(event, other)

    def start_mode_events(self, event):
        menu = self.menu.services
        greetings = split_str_to_list(self._BOT_CONFIG['greetings'])
        farewells = split_str_to_list(self._BOT_CONFIG['farewells'])
        # if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        if event.type == VkBotEventType.MESSAGE_NEW:
            self.print_message_description(event)
            # text = event.text.lower()
            text = event.message['text'].lower()
            # Oтветы:
            if text:
                if event.from_user:
                    # Если клиент пользователя не поддерживает callback-кнопки, нажатие на них будет
                    # отправлять  текстовые сообщения. Т.е. они будут работать как обычные inline кнопки.
                    if "callback" not in event.obj.client_info["button_actions"]:
                        print(f'Клиент user_id{event.obj.message["from_id"]} не поддерживает callback-кнопки.')
                try:
                    if text in greetings:
                        greeting = greetings[randrange(len(greetings))]
                        message = '{},\n{}!\n :))'.format(greeting.upper(), self.get_user_name(event))
                        self.start_mode(event, message, inline=True)
                    elif text in farewells:
                        farewell = farewells[randrange(len(farewells))]
                        self.send_msg(event, f'{farewell.upper()},\n{self.get_user_name(event)}!\n :))')
                    elif text == menu['matchmaker']['command'].lower() or text == menu['matchmaker']['button'].lower():
                        self.menu.switch('matchmaker')
                        self.start_mode(event, 'Спасибо за компанию,\n{}!'.format(self.get_user_name(event)))
                        self.send_msg_use_bot_dialog(event)
                    else:
                        self.start_mode(event, 'Не понимаю...', inline=True)
                except KeyError as key_err:
                    self.my_except(event, key_err, f'Попытка взять значение по ошибочному ключу {key_err}', menu)
                except Exception as other:
                    self.my_except(event, other)

        elif event.type == VkBotEventType.MESSAGE_REPLY:
            print('\nНовое сообщение:')
            print('От меня для: ', end='')
            print(event.obj.peer_id)
            print('Текст:\n', event.obj.text.lower())
            print()

        elif event.type == VkBotEventType.MESSAGE_TYPING_STATE:
            print('\nПечатает ', end='')
            print(event.message['from_id'], end=' ')
            print('для ', end='')
            print(event.message['to_id'])
            print()

        elif event.type == VkBotEventType.GROUP_JOIN:
            print('\n', event.message['from_id'], end=' ')
            print('Вступил в группу!')
            print()

        elif event.type == VkBotEventType.GROUP_LEAVE:
            print('\n', event.message['from_id'], end=' ')
            print('Покинул группу!')
            print()

        elif event.type == VkBotEventType.MESSAGE_EVENT:
            # Callback кнопки не срабатывают: события не происходит ???
            print(event.type)
            print()

        else:
            print(event.type)
            print()

    def start_mode(self, event, message='', inline=False, callback=False):
        post = {'peer_id': event.message['peer_id'], 'random_id': get_random_id(),
                'message': message if event.from_chat else f'{message} Текущий{self.menu}'}
        if not event.from_chat:
            post['keyboard'] = self.get_keyboard(inline=inline, callback=callback)
        self.send_post(post)
        return post

    def exit(self, event, callback=False) -> bool:
        menu = self.menu.services
        # text = event.text.lower()
        text = event.message['text'].lower()
        if text == menu['exit']['button'].lower() or text == menu['exit']['command'].lower():
            message = '{},\nсервис "{}" закрыт!'.format(self.get_user_name(event), self.menu.button)
            self.menu.exit()
            self.start_mode(event, message, callback=callback)
            return True
        return False

    def send_filter(self, event, message=''):
        """" Сообщение пользователю о выбранных фильтрах стандартного поиска подходящих пиплов """
        std_filter = self.menu.get_filter_string()
        message += '\n{}:\t{}'.format(self.menu.button, std_filter if std_filter else 'фильтр не задан...')
        post = {'peer_id': event.message["peer_id"], 'random_id': get_random_id(), 'message': message,
                'keyboard': self.get_keyboard()}
        self.send_post(post)
        print(message)
        return post

    def send_msg(self, event, message, keyboard=None):
        """" Получает id пользователя ВК <user_id>, и сообщение ему """
        post = {'peer_id': event.message["peer_id"], 'random_id': get_random_id(), 'message': message}
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
            self.send_msg(event, '{} Юзать сервис переходи в чат с @{}!'.format(
                f'{self.get_user_name(event)}!\n', self._BOT_CONFIG["name"]))

    def print_message_description(self, event):
        msg = f'\nНовое сообщение\t{event.t}:'
        msg += f'из чата {event.chat_id}' if event.from_chat else ''
        msg += f'\nот: {self.get_user_title(event)}'
        msg += f' *--- {event.message["text"]}'
        print(msg)
        # print('*---', event.from_user, event.from_chat, event.from_group, event.from_me)
        return msg

    def get_user(self, event, name_case='nom', fields="city"):
        """ Получаем пользователя """
        user_id = event.message['from_id']
        return self.vk_api_methods.users.get(user_ids=user_id, fields=fields, name_case=name_case)[0]

    def get_user_name(self, event, name_case='nom'):
        """ Получаем имя пользователя"""
        user = self.get_user(event, name_case)
        return f'{user["first_name"]} {user["last_name"]}'

    def get_user_city(self, event):
        """ Получаем город пользователя"""
        user = self.get_user(event)
        return user["city"]

    def get_user_title(self, event):
        """ Получаем кратко пользователя"""
        user = self.get_user(event, 'gen')
        return f'{user["last_name"]} {user["first_name"]} (id = {event.message["from_id"]})'
        #        f'{user["city"]["title"]} (id = {user_id})'
