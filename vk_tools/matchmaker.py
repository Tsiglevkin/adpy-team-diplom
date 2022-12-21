#  Модуль в разработке

from datetime import date

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from vk_tools.vk_bot import VkBot
from vk_tools.standard_checker import StandardChecker, get_standard_filter
from vk_tools.free_user_case_checker import LegitimacyUserChecker
from bot_config.config import get_config
from db_tools import orm_models as orm
from db_tools.orm_models import VKinder, VkIdol
from vk_tools.checker import VkUserChecker


class Matchmaker(VkBot):
    """ Выполняет поиск, показ и сохранение/бан выбранных из подходящих юзверей    """

    def __init__(self, bot='bot.cfg', db='db.cfg'):
        super().__init__(bot)
        self._DB_CONFIG: dict = get_config('db', db)
        self.engine = sqlalchemy.create_engine(self.get_DSN())  # <class 'sqlalchemy.engine.base.Engine'>
        self.SessionLocal = sessionmaker(bind=self.engine)  # <class 'sqlalchemy.orm.session.sessionmaker'>
        self.db: Session = None
        self.checkers = []
        self.client_id = None
        self.chosen_vk_users = None
        if bool(self._DB_CONFIG['overwrite']):
            orm.drop_tables(self.engine)
        orm.create_tables(self.engine)
        print('A database {} with tables has been created, access is open.'.format(self._DB_CONFIG['dbase name']))

    def get_DSN(self) -> str:
        db = self._DB_CONFIG
        return 'postgresql://{}:{}@{}/{}'.format(db["login"], db["password"], db["server"], db["dbase name"])

    def add_checker(self, checker: object) -> list:
        self.checkers.append(checker)
        return self.checkers

    def search_advisable_users(self, client_id: int, search_filter: dict):
        """
        Подключение разных фильтров и интерфейса
        :param client_id:
        :param search_filter:
        :return:
        """
        self.client_id = client_id
        if not self.db:
            self.db = self.SessionLocal()

        old_client = self.db.query(VKinder).filter(VKinder.vk_id == client_id).first()
        if not old_client:
            print(f'Новый клиент {client_id}!')
            self.db.add(VKinder(vk_id=client_id, first_visit_date=date.today()))
        self.chosen_vk_users = self.db.query(VkIdol).filter(VkIdol.vk_id == client_id)
        ban = self.chosen_vk_users.filter(VkIdol.ban)
        self.add_checker(LegitimacyUserChecker(user_ids=(user.vk_idol_id for user in self.chosen_vk_users),
                                               ban_ids=(ban_user.vk_idol_id for ban_user in ban)))
        #        ----------  Стандартный поиск  -----------
        bot_filter: dict = get_standard_filter(search_filter=search_filter)
        print('\n------ {}:\t'.format(search_filter['standard']['description'].strip().upper()), end='')
        if bot_filter['buttons']:
            print(bot_filter['buttons'])
            self.add_checker(StandardChecker(client_id=client_id, search_filter=search_filter,
                                             api_methods=self.vk_api_methods))
        else:
            print('Стандартный фильтр не задан...')

        #   ----------  Поиск по интересам  -----------
        #   InterestChecker
        #
        #   ----------  Продвинутый поиск  -----------
        #   AdvancedChecker
        #

        self.menu.service['last_one_found_id'] = 0
        self.event.message['text'] = self.menu.services['next']['button']  # 'СЛЕДУЮЩИЙ'
        self.search_advisable_mode_events()

    def search_advisable_mode_events(self, requests_block=10, requests_step=1):
        """
        Поиск (прогон по фильтрам), просмотр и выбор подходящих и забаненных пользователей
        :param requests_block: кол-во пользователей в api-запросах
        :param requests_step: шаг проверяемых в блоке api-запроса
        :return: user (из полученного json)
        """
        menu = self.menu.services
        api_fields = 'sex,city,bdate,counters'

        def check_user(user: dict) -> bool:
            """
            Работа фмльтров (подходит ли пользователь по выбранным условиям)
            :param user: из json
            :return:
            """
            for checker in self.checkers:
                if not checker.is_advisable_user(user):
                    return False
            return True

        def db_close():
            """
            Сохранение в базу и закрытие текущей локальной сессии
            :return: err
            """
            try:
                err = ''
                self.db.commit()
                self.db.close()
            except Exception as err:
                print(err)
            return err

        def next_button() -> dict:
            """
            Операция "Следующий"
            :return: user (из полученного json)
            """
            last_id = self.menu.service['last_one_found_id']
            number_block = 0
            while True:
                next_id_block = ','.join(str(next_id) for next_id in range(
                    last_id + 1, last_id + requests_block, requests_step))
                users = self.vk_api_methods.users.get(user_ids=next_id_block, fields=api_fields)
                if not users:
                    print('\tПоздравляем, ты всех перебрал, кто подходил под твои условия!')
                    db_close()
                    return {}
                for user in users:
                    if check_user(user):
                        self.menu.service['last_one_found_id'] = user['id']
                        self.send_msg(peer_id=self.client_id, keyboard=self.get_keyboard(inline=True),
                                      message='Нашли {}'.format(self.get_user_title(user_id=user["id"])))
                        return user
                last_id += requests_step
                number_block += 1
                if number_block % 20 == 0:
                    self.send_msg(message='Терпение! Идёт поиск подходящих пиплов...')
            ###

        if self.event.type == VkBotEventType.MESSAGE_NEW:
            self.print_message_description()
            text = self.event.message['text'].lower()
            user_id = self.menu.service['last_one_found_id']
            # Oтветы:
            try:
                if self.event.from_chat:
                    self.send_msg_use_bot_dialog()
                elif text == menu['next']['command'].lower() or text == menu['next']['button'].lower():
                    if not next_button():
                        self.exit()
                elif text == menu['save']['command'].lower() or text == menu['save']['button'].lower():
                    self.db.add(VkIdol(vk_idol_id=user_id, vk_id=self.client_id, ban=False, rec_date=date.today()))
                    if not next_button():
                        self.exit()
                elif text == menu['ban']['command'].lower() or text == menu['ban']['button'].lower():
                    self.db.add(VkIdol(vk_idol_id=user_id, vk_id=self.client_id, ban=True, rec_date=date.today()))
                    if not next_button():
                        self.exit()
                elif self.exit():
                    db_close()
                else:
                    if not self.event.from_chat:
                        self.start_mode(message='Не понимаю...')
            except KeyError as key_err:
                self.my_except(key_err, f'Попытка взять значение по ошибочному ключу {key_err}'
                                        f' в search_advisable_mode_events', menu)
                raise key_err
            except Exception as other:
                self.my_except(other)
                # raise other
