#

from pprint import pprint

import sqlalchemy
from sqlalchemy.orm import sessionmaker

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from vk_tools.vk_bot import VkBot
from vk_tools.standard_checker import StandardChecker, get_standard_filter
from bot_config.config import get_config
from db_tools import orm_models as orm
from db_tools.orm_models import VkGroup, Advisable
from vk_tools.checker import VkUserChecker


class Matchmaker(VkBot):

    def __init__(self, bot='bot.cfg', db='db.cfg'):
        super().__init__(bot)
        self._DB_CONFIG: dict = get_config('db', db)
        self.engine = sqlalchemy.create_engine(self.get_DSN())  # <class 'sqlalchemy.engine.base.Engine'>
        self.SessionLocal = sessionmaker(bind=self.engine)  # <class 'sqlalchemy.orm.session.sessionmaker'>
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

    def refresh_group_users(self) -> list:
        db = self.SessionLocal()
        if not (db and self.group_id and self.vk_tools):
            print(f'Недостаточно параметров! db, group, tools\t-> {db}, {self.group_id}, {self.vk_tools} ...')
            return []
        print('\nRecording new users of VK group...')
        vk_users_added = []
        while True:
            vk_group_users_right_now = self.vk_tools.get_all('groups.getMembers', 1000,
                                                             {'group_id': self.group_id})['items']
            pprint(vk_group_users_right_now)
            vk_users_added += list(vk_id for vk_id in vk_group_users_right_now if
                                   not db.query(VkGroup).filter(VkGroup.id == vk_id).first())
            db.add_all(VkGroup(id=vk_id) for vk_id in vk_users_added)
            print('Added  to the VK group:', vk_users_added if vk_users_added else 'has no new users!')
            break
        for user in db.query(Advisable).all():
            db.delete(user)
        db.commit()
        db.close()
        print('Congratulations! The updated list of users of the group has been read and recorded in the database.')
        print('Deleted records in Advisable')
        return vk_users_added

    def search_advisable_users(self, client_id: int, search_filter: dict, select_mode=True, search_mode='No mass requests'):
        self.client_id = client_id
        self.refresh_group_users()
        # db: Session = Depends(Matchmaker.get_db(self.SessionLocal))
        if search_mode != "No mass requests":
            pass
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

        if not select_mode:
            db = self.SessionLocal()  # db: Session
            self.refresh_group_users()
            if len(self.checkers):
                db.add_all(Advisable(id=user.id) for user in db.query(VkGroup).all()
                           if self.check_user(vk_id=user.id))
            else:
                print('No checkers have been created!')
                db.add_all(Advisable(id=user.id) for user in db.query(VkGroup).all())
            advisable_users = list(user.id for user in db.query(Advisable).all())
            print(f'\n{advisable_users} --> {len(advisable_users)} was pulled into Advisable')
            db.commit()
            db.close()
            return advisable_users

        self.menu.service['last_one_found_id'] = 0
        self.event.message['text'] = self.menu.services['next']['button']  # 'СЛЕДУЮЩИЙ'
        self.search_advisable_mode_events()

    def check_user(self, vk_id: int):
        return len(self.checkers) == sum(checker.is_advisable_user(vk_id=vk_id) for checker in self.checkers)

    def search_advisable_mode_events(self):
        menu = self.menu.services
        db = self.SessionLocal()

        def next_button():
            next_candidate = db.query(VkGroup
                ).filter(
                    self.check_user(vk_id=VkGroup.id)  # IndexError: list index out of range ????? то есть, то нет err
                ).filter(
                    VkGroup.id > self.menu.service['last_one_found_id']
                ).first()
            if next_candidate:
                self.menu.service['last_one_found_id'] = next_candidate.id
                self.send_msg(peer_id=self.client_id, message=self.get_user_title(user_id=next_candidate.id),
                              keyboard=self.get_keyboard(inline=True))
            return next_candidate

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
                    current_candidate = db.get(VkGroup, self.menu.service['last_one_found_id'])
                    db.add(Advisable(id=current_candidate.id, liked=True))
                    if not next_button():
                        self.exit()
                elif self.exit():
                    pass
                else:
                    if not self.event.from_chat:
                        self.start_mode(message='Не понимаю...')
            except KeyError as key_err:
                self.my_except(key_err, f'Попытка взять значение по ошибочному ключу {key_err}', menu)
            except Exception as other:
                self.my_except(other)
                raise other
            self.menu.service['last_one_found_id'] = 0
            db.commit()
            db.close()
