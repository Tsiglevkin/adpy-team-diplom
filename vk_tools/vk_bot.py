#

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
# from random import randrange
from vk_api.utils import get_random_id
from pprint import pprint


class VkBot:
    def __init__(self, bot: str = 'bot.cfg', db: str = 'db.cfg'):
        self._BOT_CONFIG = VkBot._get_bot_config(bot)
        self._DB_CONFIG = VkBot._get_db_config(db)
        self.bot_session = vk_api.VkApi(token=self._BOT_CONFIG['token'])
        self.bot_api = self.bot_session.get_api()
        print(f"Создан объект бота! (id={self.bot_session.app_id})")
        # self._COMMANDS = ["ПРИВЕТ", "ПОИСК ПАРЫ", "ПОКА"]

    def send_msg(self, user_id, message):
        """"        получает id пользователя ВК <user_id>, и сообщение ему        """
        # self.bot_api.messages.send(peer_id=user_id, message=message, random_id=get_random_id())
        self.bot_session.method('messages.send',
            {'user_id': user_id, 'message': message, 'random_id': get_random_id(), })

    def write_db_all_group_users(self):
        tools = vk_api.VkTools(self.bot_session)
        ids = tools.get_all('groups.getMembers', 1000, {'group_id': self._BOT_CONFIG['group_id']})
        count = ids['count']
        ids_list = ids['items']
        print(f'{count} членов в группе')
        pprint(ids_list)
        return ids_list

    def get_user(self, user_id, name_case='nom', fields="city"):
        """ Получаем пользователя"""
        return self.bot_api.users.get(user_ids=user_id, fields=fields, name_case=name_case)[0]

    def get_user_name(self, user_id, name_case='nom'):
        """ Получаем город пользователя"""
        user = self.get_user(user_id, name_case)
        return f'{user["first_name"]} {user["last_name"]}'

    def get_user_city(self, user_id):
        """ Получаем город пользователя"""
        user = self.get_user(user_id)
        return user["city"]["title"]

    def get_user_title(self, user_id):
        """ Получаем кратко пользователя"""
        user = self.get_user(user_id, 'gen')
        return f'{user["last_name"]} {user["first_name"]}' \
               f' (id = {user_id})'
        #        f'{user["city"]["title"]} (id = {user_id})'

    def start(self):
        # Работа с сообщениями
        longpoll = VkLongPoll(self.bot_session, group_id=self._BOT_CONFIG['group_id'])
        print('Запущен бот группы id =', longpoll.group_id)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    text = event.text.lower()
                    print('Новое сообщение:\t', end="")
                    print("личное" if event.user_id > 0 else "групповое")
                    print(f"от: {self.get_user_title(event.user_id)})")
                    print("*---", event.text)
                    # Oтветы:
                    if text == "привет":
                        self.send_msg(event.user_id, f"Хай, {self.get_user_name(event.user_id)}! :)")
                    elif text == "пока":
                        self.send_msg(event.user_id, "Чао :(")
                    elif text == "найди друзей":
                        self.send_msg(event.user_id, "Начинаю поиск друзей!")
                        self.write_db_all_group_users()
                    else:
                        self.send_msg(event.user_id, "Не понимаю...")

            elif event.type == VkBotEventType.MESSAGE_REPLY:
                print('Новое сообщение:')
                print('От меня для: ', end='')
                print(event.obj.peer_id)
                print('Текст:', event.text)
                print()

            elif event.type == VkBotEventType.MESSAGE_TYPING_STATE:
                print('Печатает ', end='')
                print(event.obj.from_id, end=' ')
                print('для ', end='')
                print(event.obj.to_id)
                print()

            elif event.type == VkBotEventType.GROUP_JOIN:
                print(event.obj.user_id, end=' ')
                print('Вступил в группу!')
                print()

            elif event.type == VkBotEventType.GROUP_LEAVE:
                print(event.obj.user_id, end=' ')
                print('Покинул группу!')
                print()

            else:
                print(event.type)
                print()

    @staticmethod
    def _get_bot_config(config_file: str = 'bot.cfg'):
        config = {}
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                config['group_name'] = file.readline().strip()
                config['group_id'] = int(file.readline().strip())
                config['token'] = file.readline().strip()
                return config
        except FileNotFoundError as ex:
            print(f'File "{config_file}" not found...\n\t{ex}\n')
        except OSError as other:
            print(f'При открытии файла "{config_file}" возникли проблемы: \n\t{other}\n')
        print('Не получилось создать бот: недостаточно информации! ')
        quit(1)

    @staticmethod
    def _get_db_config(config_file: str = 'db.cfg'):
        config = {}
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                config['login'] = file.readline().strip()
                config['password'] = file.readline().strip()
                config['dbase_name'] = file.readline().strip()
                config['dbase_scheme'] = file.readline().strip()
                config['table_vkinder_users'] = file.readline().strip()
                config['table_fanlist'] = file.readline().strip()
                config['table_stoplist'] = file.readline().strip()
                config['table_recommended'] = file.readline().strip()
                return config
        except FileNotFoundError as ex:
            print(f'File "{config_file}" not found...\n\t{ex}\n')
        except OSError as other:
            print(f'При открытии файла "{config_file}" возникли проблемы: \n\t{other}\n')
        print('Не получилось создать бот: недостаточно информации! ')
        quit(1)
