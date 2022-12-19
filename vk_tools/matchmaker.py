#

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from vk_tools.vk_bot import VkBot
from vk_tools.standard_checker import StandardChecker, get_standard_filter
from bot_config.config import get_config
from db_tools import orm_models as orm
from db_tools.orm_models import VkinderUser, MostMostUser
from vk_tools.checker import VkUserChecker


class Matchmaker(VkBot):

    def __init__(self, bot='bot.cfg', db='db.cfg'):
        super().__init__(bot)
        self._DB_CONFIG: dict = get_config('db', db)
        self.engine = sqlalchemy.create_engine(self.get_DSN())  # <class 'sqlalchemy.engine.base.Engine'>
        self.SessionLocal = sessionmaker(bind=self.engine)  # <class 'sqlalchemy.orm.session.sessionmaker'>
        self.db: Session = None
        self.checkers = []
        self.client_id = None
        if bool(self._DB_CONFIG['overwrite']):
            orm.drop_tables(self.engine)
        orm.create_tables(self.engine)
        print('A database {} with tables has been created, access is open.'.format(self._DB_CONFIG['dbase name']))

    def get_DSN(self) -> str:
        db = self._DB_CONFIG
        return 'postgresql://{}:{}@{}/{}'.format(db["login"], db["password"], db["server"], db["dbase name"])

    def add_checker(self, checker: VkUserChecker) -> list:
        self.checkers.append(checker)
        return self.checkers

    def search_advisable_users(self, client_id: int, search_filter: dict):
        self.client_id = client_id
        if not self.db:
            self.db = self.SessionLocal()
        old_client = self.db.query(VkinderUser).filter(VkinderUser.id == client_id).first()
        if not old_client:
            print(f'Новый клиент {client_id}!')
            self.db.add(VkinderUser(id=client_id))
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

    def check_user(self, vk_id: int):
        return len(self.checkers) == sum(checker.is_advisable_user(vk_id=vk_id) for checker in self.checkers)

    def search_advisable_mode_events(self, requests_step=10):
        menu = self.menu.services
        api_fields = 'sex,city,bdate,counters'

        def check_user(user: dict) -> bool:
            for checker in self.checkers:
                if not checker.is_advisable_user(user):
                    return False
            return True

        def db_close():
            self.db.commit()
            self.db.close()

        def next_button() -> dict:
            last_id = self.menu.service['last_one_found_id']
            while True:
                next_id_block = ','.join(str(next_id) for next_id in range(last_id + 1, last_id + requests_step))
                users = self.vk_api_methods.users.get(user_ids=next_id_block, fields=api_fields)
                if not users:
                    print('\tПоздравляем, ты всех перебрал, кто подходил под твои условия!')
                    db_close()
                    return {}
                for user in users:
                    ok = check_user(user)
                    if ok:
                        self.menu.service['last_one_found_id'] = user['id']
                        self.send_msg(peer_id=self.client_id, keyboard=self.get_keyboard(inline=True),
                                      message='Нашли {}'.format(self.get_user_title(user_id=user["id"])))
                        return user
                last_id += requests_step

        if self.event.type == VkBotEventType.MESSAGE_NEW:
            self.print_message_description()
            text = self.event.message['text'].lower()
            # Oтветы:
            try:
                if self.event.from_chat:
                    self.send_msg_use_bot_dialog()
                elif text == menu['next']['command'].lower() or text == menu['next']['button'].lower():
                    if not next_button():
                        self.exit()
                elif text == menu['save']['command'].lower() or text == menu['save']['button'].lower():
                    self.db.add(MostMostUser(id=self.menu.service['last_one_found_id'], ban=False))
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
