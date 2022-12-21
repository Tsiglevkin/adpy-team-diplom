# Проверяет, есть ли пользователь в списке избранных клиента


class LegitimacyUserChecker:
    """
    Проверяет, есть ли пользователь в списке избранных клиента.
    Если есть, то такой пользователь дальше не рассматривается как подходящий.
    :param user_ids: список id всех пользователей VK, избранных клиентом, включая бан.
    :param ban_ids: список id всех забаненных клиентом пользователей VK.
    :return: bool: прошел проверку - True
    """
    _skill = 'Checking the validity of new users'

    def __init__(self, user_ids: list = [], ban_ids: list = []):
        self.user_ids = user_ids
        self.ban_ids = ban_ids

    def is_advisable_user(self, user: dict) -> bool:
        user_id = user['id']
        print(f'\nid={user_id}, users={list(self.user_ids)}, ban={list(self.ban_ids)}')
        if user_id in self.user_ids:
            print(f'\t\tuser{user_id} НЕ ПРОШЁЛ:', end=' ')
            print(f'забанен клиентом!' if user_id in self.ban_ids
                  else 'уже в списке избранных!')
            return False
        print('\t\tПРОШЁЛ: еще нет в списке избранных!')
        return True
