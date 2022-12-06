import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship
from tqdm import tqdm

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    user_id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, nullable=False, unique=True)

    def __str__(self):
        return f'User with {self.user_id} has vk_id {self.vk_id}'


class Candidate(Base):
    __tablename__ = 'candidate'

    candidate_id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, nullable=False, unique=True)

    def __str__(self):  # метод str для того, чтобы корректно принтовать функцию
        return f'Candidate with id {self.candidate_id} has vk_id {self.vk_id}'


class MarkList(Base):
    __tablename__ = 'mark_list'

    user_mark_id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.user_id'), nullable=False)
    candidate_id = sq.Column(sq.Integer, sq.ForeignKey('candidate.candidate_id'), nullable=False)
    like = sq.Column(sq.Boolean, nullable=False)
    dislike = sq.Column(sq.Boolean, nullable=False)

    user = relationship(Users, backref='mark_list')
    candidate = relationship(Candidate, backref='mark_list')

    def __str__(self):  # не уверен в верности метода.
        if self.like and self.dislike is False:
            return f'Candidate {self.candidate_id} for user {self.user_id} has {self.like}'
        elif self.like is False and self.dislike:
            return f'Candidate {self.candidate_id} for user {self.user_id} has {self.dislike}'
        else:
            return f'Candidate {self.candidate_id} for user {self.user_id} has not been reviewed'


def create_tables(engine):
    Base.metadata.create_all(engine)


def drop_tables(engine):
    Base.metadata.drop_all(engine)


def show_all_candidates_id(some_session, user_vk_id: int) -> list:
    """Функция возвращает список кандидатов без отметок для конкретного пользователя"""
    res_list = []
    for c in some_session.query(Candidate.vk_id).join(MarkList.candidate).join(MarkList.user).filter(
            Users.vk_id == user_vk_id, MarkList.like == 'False', MarkList.dislike == 'False').all():
        res_list.append(c[0])
    return res_list


def show_all_like_candidates(some_session, user_vk_id: int) -> list:  # метод не проверен, сработает ли 'and'?
    """Функция выводит список кандидатов, отмеченных лайком"""
    res_list = []
    for c in some_session.query(Candidate.vk_id).join(MarkList.candidate).join(MarkList.user).filter(
            MarkList.like == 'True', Users.vk_id == user_vk_id).all():
        res_list.append(c[0])
    return res_list


def show_black_list(some_session, user_vk_id: int) -> list:
    """Функция выводит список кандидатов, отмеченных дизлайком"""
    res_list = []
    for c in some_session.query(Candidate.vk_id).join(MarkList.candidate).join(MarkList.user).filter(
            MarkList.dislike == 'True', Users.vk_id == user_vk_id).all():
        res_list.append(c[0])
    return res_list


def add_id_to_users(some_session, user_vk_id_list: list):
    """Функция добавляет пользователя в таблицу Users"""
    for id_ in tqdm(user_vk_id_list, desc='Добавляем id в БД'):
        new_user = Users(vk_id=id_)
        some_session.add(new_user)
        some_session.commit()
    return 'ID пользователей добавлены'


def add_id_to_candidates(some_session, candidate_vk_id_list: list):
    """Функция добавляет пользователя в таблицу Candidate"""
    for id_ in tqdm(candidate_vk_id_list, desc='Добавляем id в БД'):
        new_candidate = Candidate(vk_id=id_)
        some_session.add(new_candidate)
        some_session.commit()
    return 'ID кандидатов добавлены'


def add_id_to_marklist(some_session, user_vk_id: int, candidate_vk_id: int) -> str:
    """Функция добавляет пользователя в таблицу MarkList. Требуются vk_id от пользователя и кандидата"""
    if user_vk_id != candidate_vk_id:
        user_id = some_session.query(Users.user_id).filter(Users.vk_id == user_vk_id).scalar()
        candidate_id = some_session.query(Candidate.candidate_id).filter(Candidate.vk_id == candidate_vk_id).scalar()

        new_mark_candidate = MarkList(user_id=user_id, candidate_id=candidate_id, like=False, dislike=False)
        some_session.add(new_mark_candidate)
        some_session.commit()
        return f'Для пользователя с ID {user_vk_id} добавлен кандидат с ID {candidate_vk_id}.'
    else:
        return 'пользователь и кандидат - один человек, смените пожалуйста кандидата.'


def get_like(some_session, user_vk_id: int, candidate_vk_id: int) -> str:
    """Функция позволяет поставить like кандидату. Требуются vk_id от пользователя и кандидата"""
    user_id = some_session.query(Users.user_id).filter(Users.vk_id == user_vk_id).scalar()
    candidate_id = some_session.query(Candidate.candidate_id).filter(Candidate.vk_id == candidate_vk_id).scalar()

    some_session.query(MarkList).filter(MarkList.user_id == user_id, MarkList.candidate_id == candidate_id).\
        update({'like': True, 'dislike': False})
    some_session.commit()

    return f'Кандидату {candidate_vk_id} поставлен like.'


def get_dislike(some_session, user_vk_id: int, candidate_vk_id: int) -> str:
    """Функция позволяет поставить dislike кандидату. Требуются vk_id от пользователя и кандидата"""
    user_id = some_session.query(Users.user_id).filter(Users.vk_id == user_vk_id).scalar()
    candidate_id = some_session.query(Candidate.candidate_id).filter(Candidate.vk_id == candidate_vk_id).scalar()

    some_session.query(MarkList).filter(MarkList.user_id == user_id, MarkList.candidate_id == candidate_id). \
        update({'like': False, 'dislike': True})
    some_session.commit()
    return f'Кандидату {candidate_vk_id} поставлен dislike.'


def delete_mark(some_session, user_vk_id: int, candidate_vk_id: int) -> str:
    """Функция позволяет убрать отметку like или dislike кандидату. Требуются vk_id от пользователя и кандидата"""
    user_id = some_session.query(Users.user_id).filter(Users.vk_id == user_vk_id).scalar()
    candidate_id = some_session.query(Candidate.candidate_id).filter(Candidate.vk_id == candidate_vk_id).scalar()

    some_session.query(MarkList).filter(MarkList.user_id == user_id, MarkList.candidate_id == candidate_id). \
        update({'like': False, 'dislike': False})
    some_session.commit()
    return f'Кандидату {candidate_vk_id} убрана оценка.'


