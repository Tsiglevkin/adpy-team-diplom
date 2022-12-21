#

import os
import json


def get_config(type_config='bot', config_file='bot.cfg', overwrite=True):
    config_dir = '/'
    file = config_dir + config_file
    response = {}
    if overwrite:
        print(f'The file {file} will be overwrite!')
    else:
        if config_file in os.listdir(config_dir):
            print(f'The file {file} already exists. Skipped...')
        else:
            print(f'The file {file} will be record!')
            overwrite = True
    if type_config == 'bot':
        response = read_json_file(config_file, write_json_file(get_bot_config_json(), file) if overwrite else None)
    elif type_config == 'db':
        response = read_json_file(config_file, write_json_file(get_db_config_json(), file) if overwrite else None)
    elif type_config == 'bot_menu':
        response = read_json_file(config_file, write_json_file(get_bot_menu_config_json(), file) if overwrite else None)
    return response


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
        print(f'Congratulations! The config was saved to {file}')
    except OSError as other:
        print(f'There were problems opening the file {file}: \n\t{other}')
        print('Sorry, the results are not saved to a json file...')
        quit(1)
    return dict_


def get_db_config_json():
    return {
        'login': 'postgres',
        'password': '4sql%pg',
        'dbase name': 'vkinder',
        'server': 'localhost:5432',
        'scheme': 'public',
        "overwrite": False,
        'Vkinder table for VKbot fans': 'vkinders',
        'VKIdol users table': 'vk_idols',
        'VKinder connections table of db relationships': 'vk_connections'
    }


def get_bot_config_json():
    return {
        'name': 'VKinder10',
        'group_id': '217491346',
        'token': 'vk1.a.-Y1qvpVh8DSjq4SHejdoJXPf089sA5Kuqnc40NVHx1uEUxEhe0r4d9vtlaD2gX9ABtm'
                 'JlxECTemdmVRc5ZGNCe92pN76NdNjXAc4631s5-xzreQi2Ojv59BGidAJvy6VUgLEo5IlZUHGK'
                 '-1JGJir0dHY2k4bPHlky2nk0fks8miDKMrQdO2lvyhqakGVsiz1RCBF3i7hXxx_AGXWdXINew',
        'greetings': 'привет, hi, чао, вечер в хату',
        'farewells': 'пока, by, адьюс, не скучай, быть добру'
    }


def get_bot_menu_config_json():
    return {
        'mode': {
            'start-up': {
                'button': 'Вежливый',
                'command': '@@',
                'filter': '',
                'service_code': '1',
                'description': '',
                'max_buttons_peer_line': '',
                'services': {
                    'matchmaker': {
                        'button': 'НЯША',
                        'command': '/!',
                        'filter': '',
                        'service_code': '11',
                        'description': 'мои любимчики',
                        'max_buttons_peer_line': '',
                        'services': {
                            'search': {
                                'button': 'НАЙТИ',
                                'command': '/?',
                                'filter': '',
                                'service_code': '111',
                                'description': 'поиск интересных пиплов',
                                'max_buttons_peer_line': '',
                                'services': {
                                    'filter': {
                                        'button': 'Фильтр',
                                        'command': '/f',
                                        'filter': '',
                                        'service_code': '1231',
                                        'description': 'Фильтры поиска',
                                        'max_buttons_peer_line': '2',
                                        'services': {
                                            'standard': {
                                                'button': 'Стандартный',
                                                'command': '/>',
                                                'filter': '',
                                                'service_code': '12311',
                                                'description': 'Стандартный поиск',
                                                'max_buttons_peer_line': '',
                                                'services': {
                                                    'younger': {
                                                        'button': 'моложе',
                                                        'command': '/y',
                                                        'filter': '',
                                                        'filter_api_field': 'bdate',
                                                        'filter_api_field_value': '',
                                                        'filter_api_field_deviation_value': '10000',
                                                        'service_code': '123414',
                                                        'description': 'Моложе',
                                                        'max_buttons_peer_line': '',
                                                        'services': {}},
                                                    'older': {
                                                        'button': 'старше',
                                                        'command': '/o',
                                                        'filter': '',
                                                        'filter_api_field': 'bdate',
                                                        'filter_api_field_value': '',
                                                        'filter_api_field_deviation_value': '-10000',
                                                        'service_code': '123415',
                                                        'description': 'Старше',
                                                        'max_buttons_peer_line': '',
                                                        'services': {}},
                                                    'peers': {
                                                        'button': 'ровесники',
                                                        'command': '/p',
                                                        'filter': '',
                                                        'filter_api_field': 'bdate',
                                                        'filter_api_field_value': '',
                                                        'filter_api_field_deviation_value': '0',
                                                        'service_code': '123416',
                                                        'description': 'ровесники',
                                                        'max_buttons_peer_line': '',
                                                        'services': {}},
                                                    'male': {
                                                        'button': 'Муж',
                                                        'command': '/m',
                                                        'filter': '',
                                                        'filter_api_field': 'sex',
                                                        'filter_api_field_value': '2',
                                                        'filter_api_field_deviation_value': '0',
                                                        'service_code': '123411',
                                                        'description': 'Мужчина',
                                                        'max_buttons_peer_line': '',
                                                        'services': {}},
                                                    'female': {
                                                        'button': 'Жен',
                                                        'command': '/f',
                                                        'filter': '',
                                                        'filter_api_field': 'sex',
                                                        'filter_api_field_value': '1',
                                                        'filter_api_field_deviation_value': '0',
                                                        'service_code': '123412',
                                                        'description': 'Женщина',
                                                        'max_buttons_peer_line': '',
                                                        'services': {}},
                                                    'city': {
                                                        'button': 'Город',
                                                        'command': '/city:',
                                                        'filter': '',
                                                        'filter_api_field': 'city',
                                                        'filter_api_field_value': '',
                                                        'filter_api_field_deviation_value': '0',
                                                        'service_code': '123417',
                                                        'description': 'Твой город',
                                                        'max_buttons_peer_line': '',
                                                        'services': {}},
                                                    'exit': {
                                                        'button': 'Сохранить',
                                                        'command': '/:',
                                                        'filter': '',
                                                        'filter_api_field': '',
                                                        'filter_api_field_value': '',
                                                        'filter_api_field_deviation_value': '0',
                                                        'service_code': '12319',
                                                        'description': 'Выход из режима настройки фильтров',
                                                        'max_buttons_peer_line': '',
                                                        'services': {}}
                                                }},
                                            'interests': {
                                                'button': 'По интересам',
                                                'command': '/!',
                                                'filter': '',
                                                'service_code': '12312',
                                                'description': 'Поиск по интересам',
                                                'max_buttons_peer_line': '',
                                                'services': {}},
                                            'advanced': {
                                                'button': 'Продвинутый',
                                                'command': '/++',
                                                'filter': '',
                                                'service_code': '12313',
                                                'description': 'Продвинутый поиск',
                                                'max_buttons_peer_line': '',
                                                'services': {}},
                                            'exit': {
                                                'button': 'Применить фильтр',
                                                'command': '/:',
                                                'filter': '',
                                                'service_code': '12314',
                                                'description': 'Выход из режима фильтров поиска',
                                                'max_buttons_peer_line': '',
                                                'services': {}}
                                        }},
                                    'advisable': {
                                        'button': 'ПОИСК',
                                        'command': '/?',
                                        'filter': '',
                                        'service_code': '1232',
                                        'description': 'Рекомендуем',
                                        'max_buttons_peer_line': '2',
                                        'last_one_found_id': 0,
                                        'services': {
                                            'save': {
                                                'button': 'Нравится',
                                                'command': '/+',
                                                'filter': '',
                                                'service_code': '12321',
                                                'description': '',
                                                'max_buttons_peer_line': '',
                                                'services': {}},
                                            'ban': {
                                                'button': 'В бан!',
                                                'command': '/-',
                                                'filter': '',
                                                'service_code': '12322',
                                                'description': '',
                                                'max_buttons_peer_line': '',
                                                'services': {}},
                                            'next': {
                                                'button': 'Следующий',
                                                'command': '/>',
                                                'filter': '',
                                                'service_code': '12323',
                                                'description': '',
                                                'max_buttons_peer_line': '',
                                                'services': {}},
                                            'exit': {
                                                'button': 'Выход',
                                                'command': '/:',
                                                'filter': '',
                                                'service_code': '12324',
                                                'description': 'Выход из режима просмотра результатов поиска',
                                                'max_buttons_peer_line': '',
                                                'services': {}}
                                        }},
                                    'exit': {
                                        'button': 'Выход',
                                        'command': '/:',
                                        'filter': '',
                                        'service_code': '1233',
                                        'description': 'Выход из режима поиска подходящих пользователей',
                                        'max_buttons_peer_line': '',
                                        'services': {}}
                                }},
                            'print': {
                                'button': 'Список',
                                'command': '/!',
                                'filter': '',
                                'service_code': '112',
                                'description': 'СПИСОК моих пиплов',
                                'max_buttons_peer_line': '',
                                'services': {}},
                            'exit': {
                                'button': 'Выход',
                                'command': '/:',
                                'filter': '',
                                'service_code': '113',
                                'description': '',
                                'max_buttons_peer_line': '',
                                'services': {}}}}}}}
    }
