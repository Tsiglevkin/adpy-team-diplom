#

from abc import ABC, abstractmethod
from pprint import pprint

from vk_api.vk_api import VkApiMethod


class VkUserChecker(ABC):
    _skill = 'A matchmaker Search Engine'

    def __init__(self, client_id: int, api_methods: VkApiMethod, search_filter: dict, skill=_skill):
        self.vk_api_methods = api_methods
        self.__search_filter = search_filter
        self.api_fields = 'sex,city,bdate,counters'
        self.client_id = client_id
        self.client_info = self.get_client_info()
        self.user_id = None
        self.user_info = None
        self.skill = skill
        print(self.skill, 'has been created')

    @property
    def search_filter(self):
        return self.__search_filter

    @search_filter.setter
    def search_filter(self, search_filter: dict):
        self.__search_filter = search_filter

    def get_client_info(self, client_info_fields='sex,city,bdate,counters'):
        return self.vk_api_methods.users.get(user_ids=self.client_id, fields=client_info_fields)[0]

    def get_user_info(self, user_info_fields='sex,city,bdate,counters') -> dict:
        return self.vk_api_methods.users.get(user_ids=self.user_id, fields=user_info_fields)[0]

    def __str__(self):
        user = self.get_user_info()
        return "user{}: {} {} ({}) {} {}".format(
            user['id'], user.get('first_name', ''), user.get('last_name', ''),
            ['', 'жен', 'муж'][int(user.get('sex', ''))] if user.get('sex', '') else '',
            user.get('bdate', ''),
            user.get('city', '')['title'] if user.get('city', '') else '')

    @abstractmethod
    def is_advisable_user(self, vk_id: int) -> bool:
        self.user_id = vk_id
        self.user_info = self.get_user_info()
