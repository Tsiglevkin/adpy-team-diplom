#
import queue
from config import get_bot_config
from pprint import pprint


class VkBotMenu:
    def __init__(self, menu):
        self.base_menu = menu
        self.service_name = 'start-up'
        self.is_advanced = 0
        self.service = menu[self.service_name]
        self.menu = queue.LifoQueue()
        self.read_menu()

    def read_menu(self):
        self.button = self.service['button']
        self.command = self.service['command']
        self.service_code = self.service['service_code']
        self.description = self.service['description']
        self.services = self.service['services']
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

    def get_button_list(self):
        return list(self.services[service]['button'] for service in self.services)

    def switch(self, service=''):
        if service in self.services:
            service_title = '{} {}'.format(self.service_name, self.get_button_list())
            self.menu.put({self.service_name: self.service})
            self.is_advanced += 1
            self.service_name = service
            self.service = self.services[service]
            self.read_menu()
            print(service_title, ' -> ', self.service_name, self.get_button_list())
        else:
            print(f'Сервиса "{service.upper()}" у модуля "{self.service_name}"не существует!')
        return self.service_name

    def exit(self):
        if self.is_advanced:
            service_title = '{} {}'.format(self.service_name, self.get_button_list())
            last_service: dict = self.menu.get()
            for name, service in last_service.items():
                self.service_name = name
                self.service = service
            self.is_advanced -= 1
            self.read_menu()
            print(service_title, ' -> ', self.service_name, self.get_button_list())
        else:
            print(f'Закрытие сервиса "{self.service_name.upper()}" не предусмотрено!')
            pprint(self.service)
        return self.service_name

    @staticmethod
    def display_menu(self):
        return None
