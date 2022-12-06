#

import os
import json


def get_bot_config(config_file: str = 'bot.cfg'):
    return read_json_file(config_file, write_json_bot_config(config_file))


def get_db_config(config_file: str = 'db.cfg'):
    return read_json_file(config_file, write_json_db_config(config_file))


def read_json_file(file, dict_: dict = None):
    if dict_:
        return dict_
    try:
        with open(file, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError as ex:
        print(f'File "{file}" not found...\n\t{ex}\n')
    except OSError as other:
        print(f'При открытии файла "{file}" возникли проблемы: \n\t{other}\n')
    print('Не получилось создать бот: недостаточно информации! ')
    quit(1)


def write_json_file(dict_, file):
    try:
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(dict_, f, ensure_ascii=False, indent=2)
        print(f'Congratulations! The bot config are saved to {file}')
    except OSError as other:
        print(f'There were problems opening the file {file}: \n\t{other}')
        print('Sorry, the results are not saved to a json file...')
        quit(1)
    return dict_


def write_json_db_config(config_file: str = 'db.cfg', overwrite: bool = False):
    if overwrite:
        print(f'The file {config_file} will be overwrite!')
    elif config_file in os.listdir():
        print(f'The file {config_file} already exists. Skipped...')
        return {}
    write_json_file(get_db_config_dict(), config_file)


def write_json_bot_config(config_file: str = 'bot.cfg', overwrite: bool = True):
    if overwrite:
        print(f'The file {config_file} will be overwrite!')
    elif config_file in os.listdir():
        print(f'The file {config_file} already exists. Skipped...')
        return {}
    write_json_file(get_bot_config_dict(), config_file)


def get_db_config_dict():
    return {
        'login': 'postgres',
        'password': 'postgres',
        'dbase_name': 'vkinder',
        'server': 'localhost:5432',
        'scheme': 'public',
        'table_vkinder': 'vk',
        'table_vkinder_favorite': 'vk_favorite',
        'table_vkinder_disliked': 'vk_disliked',
        'table_favorite': 'favorite',
        'table_disliked': 'disliked',
        'table_advisable': 'advisable'
    }


def get_bot_config_dict():
    return {
        'name': 'VKinder10',
        'group_id': '217491346',
        'token': 'vk1.a.-Y1qvpVh8DSjq4SHejdoJXPf089sA5Kuqnc40NVHx1uEUxEhe0r4d9vtlaD2gX9ABtm'
                 'JlxECTemdmVRc5ZGNCe92pN76NdNjXAc4631s5-xzreQi2Ojv59BGidAJvy6VUgLEo5IlZUHGK'
                 '-1JGJir0dHY2k4bPHlky2nk0fks8miDKMrQdO2lvyhqakGVsiz1RCBF3i7hXxx_AGXWdXINew',
        'greetings': 'привет, hi, чао, вечер в хату',
        'farewells': 'пока, by, адьюс, не скучай, быть добру',
        'mode': {
            'start-up': {
                'button': 'Вежливый',
                'command': '@@',
                'description': '',
                'services': {
                    'matchmaker': {
                        'button': 'НЯША',
                        'command': '@@/!',
                        'description': 'мои любимчики в группе',
                        'services': {
                            'search': {
                                'command': '@@/?',
                                'button': 'НАЙТИ',
                                'description': 'поиск интересных членов группы',
                                'services': {
                                    'next': {
                                        'command': '@@/>',
                                        'button': 'Следующий',
                                        'description': '',
                                        'services': {}},
                                    'save': {
                                        'command': '@@/+',
                                        'button': 'Сохранить',
                                        'description': '',
                                        'services': {}},
                                    'exit': {
                                        'command': '@@/',
                                        'button': 'Выход',
                                        'services': {}}
                                }},
                            'print': {
                                'command': '@@/!',
                                'button': 'Список',
                                'services': {}},
                            'exit': {
                                'command': '@@/',
                                'button': 'Выход',
                                'services': {}}}}}}}
    }