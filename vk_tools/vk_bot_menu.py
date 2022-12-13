#

import queue
from pprint import pprint

from bot_config.config import get_config


class VkBotMenu:
    def __init__(self, menu='bot_menu.cfg'):
        self.base_menu: dict = get_config('bot_menu', menu)['mode']
        self.service_name = 'start-up'
        self.is_advanced = 0
        self.service = self.base_menu[self.service_name]
        self.menu = queue.LifoQueue()
        self.read_menu()

    def read_menu(self):
        self.button = self.service['button']
        self.command = self.service['command']
        self.filter = self.service['filter']
        self.service_code = self.service['service_code']
        self.description = self.service['description']
        self.services = self.service['services']
        self.max_button = 3
        try:
            self.max_button = int(self.service['max_buttons_peer_line'])
        except ValueError as err:
            pass
            # print(err, f'max_button присвоено значение {self.max_button}')
        return self.service

    def menu_title(self):
        comment = f'\n*\t{self.description.strip().lower()}\t*' if self.description else ''
        return "\nсервис {}:{}".format(self.button.upper(), comment)

    def __str__(self):
        services = self.menu_title()
        for service in self.services:
            activity = self.services[service]
            services += '\n-\t{}\t(\t{}\t)'.format(activity['button'].upper(), activity['command'])
        return services

    def get_buttons(self):
        return {'max': self.max_button,
                'buttons': list(self.services[service]['button'] for service in self.services),
                'filter': list(self.services[service]['filter'] for service in self.services)}

    def get_filter_string(self, param=''):
        buttons = self.get_buttons()
        lst = list(button for num, button in enumerate(buttons['buttons']) if buttons['filter'][num])
        return lst if param else ', '.join(lst)

    def switch(self, service=''):
        if service in self.services:
            service_title = '{} {}'.format(self.service_name, self.get_buttons()['buttons'])
            self.menu.put({self.service_name: self.service})
            self.is_advanced += 1
            self.service_name = service
            self.service = self.services[service]
            self.read_menu()
            print(service_title, ' -> ', self.service_name, self.get_buttons()['buttons'])
        else:
            print(f'Сервиса "{service.upper()}" у модуля "{self.service_name}"не существует!')
        return self.service_name

    def exit(self):
        if self.is_advanced:
            service_title = '{} {}'.format(self.service_name, self.get_buttons()['buttons'])
            last_service: dict = self.menu.get()
            for name, service in last_service.items():
                self.service_name = name
                self.service = service
            self.is_advanced -= 1
            self.read_menu()
            print(service_title, ' -> ', self.service_name, self.get_buttons()['buttons'])
        else:
            print(f'Закрытие сервиса "{self.service_name.upper()}" не предусмотрено!')
            pprint(self.service)
        return self.service_name
