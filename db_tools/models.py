import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    user_id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, nullable=False)

    def __str__(self):
        return f'User with {self.user_id} has vk_id {self.vk_id}'


class Candidate(Base):
    __tablename__ = 'candidate'

    candidate_id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, nullable=False)

    def __str__(self):  # метод str для того, чтобы корректно принтовать функцию
        return f'Candidate with {self.candidate_id} has vk_id {self.vk_id}'


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


def show_all_candidates_id(some_session, some_user_vk_id: int) -> list:
    """Функция возвращает список кандидатов для конкретного пользователя"""
    return some_session.query(Candidate.vk_id).join(MarkList.candidate).join(MarkList.user).filter(
            Users.vk_id == some_user_vk_id)


def show_all_like_candidates(some_session, some_user_vk_id: int) -> list:  # метод не проверен, сработает ли 'and'?
    """Функция выводит список кандидатов, отмеченных лайком"""
    return some_session.query(Candidate.vk_id).join(MarkList.candidate).join(MarkList.user).filter(
            MarkList.like is True and Users.vk_id == some_user_vk_id)


def show_black_list(some_session, some_user_vk_id: int) -> list:
    """Функция выводит список кандидатов, отмеченных дизлайком"""
    return some_session.query(Candidate).join(MarkList.candidate).join(MarkList.user).filter(
            MarkList.dislike is True and Users.vk_id == some_user_vk_id)


def add_id_to_users(some_session, user_vk_id: int) -> str:
    """Функция добавляет пользователя в таблицу Users"""
    new_user = Users(vk_id=user_vk_id)
    some_session.add(new_user)
    some_session.commit()
    return f'Пользователь с id {user_vk_id} добавлен в таблицу Users'


def add_id_to_candidates(some_session, user_vk_id: int) -> str:
    """Функция добавляет пользователя в таблицу Candidate"""
    new_candidate = Candidate(vk_id=user_vk_id)
    some_session.add(new_candidate)
    some_session.commit()
    return f'Пользователь с id {user_vk_id} добавлен в таблицу Candidate'


def get_like(some_session, user_vk_id: int, vk_candidate_id: int) -> str:
    """Функция позволяет поставить like кандидату"""
    marked_candidate = MarkList(user_id=user_vk_id, candidate_id=vk_candidate_id, like=True, dislike=False)
    some_session.add(marked_candidate)
    some_session.commit()
    return f'Кандидату {vk_candidate_id} поставлен like.'


def get_dislike(some_session, user_vk_id: int, vk_candidate_id: int) -> str:
    """Функция позволяет поставить dislike кандидату"""
    marked_candidate = MarkList(user_id=user_vk_id, candidate_id=vk_candidate_id, like=False, dislike=True)
    some_session.add(marked_candidate)
    some_session.commit()
    return f'Кандидату {vk_candidate_id} поставлен dislike.'

