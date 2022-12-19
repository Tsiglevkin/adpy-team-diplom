#

from vk_tools.checker import VkUserChecker
from vk_api.vk_api import VkApiMethod


class InterestChecker(VkUserChecker):
    _skill = 'An interest matchmaker Search Engine'

    def __init__(self, client_id: int, api_methods: VkApiMethod, search_filter: dict):
        super(InterestChecker, self).__init__(client_id, api_methods, search_filter, self._skill)

    def is_advisable_user(self, user: dict) -> bool:
        super(InterestChecker, self).is_advisable_user(user)
        return True
