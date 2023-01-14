from pyrogram import Client
import configparser
import os.path
import sys


RED_COLOR = "\033[1;31m"
GREEN_COLOR = "\033[1;32m"
BLUE_COLOR = "\033[1;36m"
PURPLE_COLOR = "\033[1;35m"

api_id = []
api_hash = []
api_name = []
ad_msg = None
ad_photo = None
ad_video = None
app = None
config = configparser.ConfigParser()


def save_default(api_id, api_hash, api_name):
    global config
    api_names = ""
    config['DEFAULT'] = {}
    for i in range(len(api_name)):
        api_names += api_name[i] + " "
        config['DEFAULT']['api_id_' + api_name[i]] = api_id[i]
        config['DEFAULT']['api_hash_' + api_name[i]] = api_hash[i]
    config['DEFAULT']['api_names'] = api_names


def save_content(ad_msg, ad_photo, ad_video):
    global config
    config['CONTENT'] = {
        'ad_msg': ad_msg[:-1],
        'ad_photo': ad_photo,
        'ad_video': ad_video
    }


def change_default_selection():
    global api_id, api_hash, api_name
    while True:
        code = input(GREEN_COLOR + '[+] Изменить все аккаунты? (y/n): ' + BLUE_COLOR)
        if code == 'y':
            setup_default()
            change_all_default(api_id, api_hash, api_name)
            break
        elif code == 'n':
            change_default()
            break
        else:
            print(RED_COLOR + '[!] Введеный неверный символ!')


def change_default():
    global config
    config.read('config.ini')
    
    api_names = config['DEFAULT']['api_names'].split(" ")

    print(GREEN_COLOR + '[+] Выберите аккаунт: ')
    counter = 0

    for name in api_names:
        counter += 1
        print("---[" + str(counter) + "] " + name)
        
    while True:
        profile_to_change = int(input(GREEN_COLOR + '[+] Введите номер аккаунта: ' + BLUE_COLOR))
        if profile_to_change < 1 or profile_to_change > counter:
            print(RED_COLOR + '[!] Введеный неверный номер!')
        else:
            code = input(GREEN_COLOR + f'[+] Изменить {api_names[profile_to_change - 1]} аккаунт? (y/n): ' + BLUE_COLOR)
            if code == 'y':
                path = f'{api_names[profile_to_change - 1]}.session'
                os.remove(path)
                break
            elif code == 'n':
                pass
            else:
                print(RED_COLOR + '[!] Введеный неверный символ!')

    while True:
        api_id = input(GREEN_COLOR + f'[+] Введите api_id: ' + BLUE_COLOR)
        api_hash = input(GREEN_COLOR + f'[+] Введите api_hash : ' + BLUE_COLOR)
         
        try:
            with Client(api_names[profile_to_change - 1], api_id, api_hash) as app:
                app.send_message("me", "Инициализация бота!")
            break
        except:
            print(RED_COLOR + f"[-] [{api_names[profile_to_change - 1]}] Данные api_id и api_hash неверны или профиль заблокирован!")

    api_id_name = 'api_id_' + api_names[profile_to_change - 1]
    api_hash_name = 'api_hash_' + api_names[profile_to_change - 1]

    config.set('DEFAULT', api_id_name, api_id)
    config.set('DEFAULT', api_hash_name, api_hash)
    print(GREEN_COLOR + f"[+] Аккаунт {api_names[profile_to_change - 1]} был изменен!")


def change_all_default(api_id, api_hash, api_name):
    global config
    config.read('config.ini')
    config['DEFAULT'] = {}
    save_default(api_id, api_hash, api_name)

def change_content(ad_msg, ad_photo, ad_video):
    global config
    config.read('config.ini')
    config.set('CONTENT', 'ad_msg', ad_msg[:-1])
    config.set('CONTENT', 'ad_photo', ad_photo)
    config.set('CONTENT', 'ad_video', ad_video)


def setup_default():
    global api_id, api_hash, app, api_name
    profile_num = input(GREEN_COLOR + '[+] Введите количество аккаунтов: ' + BLUE_COLOR)
    for i in range(int(profile_num)):
        while True:
            api_id.append(
                input(GREEN_COLOR + f'[+] Введите api_id №{i+1}: ' + BLUE_COLOR))
            api_hash.append(
                input(GREEN_COLOR + f'[+] Введите api_hash №{i+1}: ' + BLUE_COLOR))
            api_name.append(
                input(GREEN_COLOR + f'[+] Введите имя профиля №{i+1}: ' + BLUE_COLOR))
            try:
                with Client(api_name[i], api_id[i], api_hash[i]) as app:
                    app.send_message("me", "Инициализация бота!")
                break
            except:
                print(RED_COLOR + f"[-] [{api_name[i]}] Данные api_id и api_hash неверны или профиль заблокирован!")


def setup_content():
    global ad_msg, ad_photo, ad_video
    code = ''
    while (code != 'y'):
        ad_msg = ''
        print(GREEN_COLOR + '[+] Введите текст (Enter затем Ctrl + D чтобы сохранить): ' + BLUE_COLOR)
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line == '':
                ad_msg += "\n"
            else:
                ad_msg += line + "\n"

        while True:
            ad_photo = input(
                GREEN_COLOR + '[+] Введите путь к фото (необязательно): ' + BLUE_COLOR)

            if os.path.isfile(ad_photo) or ad_photo == '':
                break
            else:
                print(RED_COLOR + '[!] Файл по данному пути не существует!')

        while True:
            ad_video = input(
                GREEN_COLOR + '[+] Введите путь к видео (необязательно): ' + BLUE_COLOR)

            if os.path.isfile(ad_video) or ad_video == '':
                break
            else:
                print(RED_COLOR + '[!] Файл по данному пути не существует!')

        while True:
            code = input(PURPLE_COLOR + '\n\n[+] Информация для отправки:\n--> Текст сообщения:\n ' + ad_msg + "\n--> Файл фото: "
             + ad_photo + "\n--> Файл видео: " + ad_video + "\n\n--> Подтвердите информацию для отправки (y/n): " + BLUE_COLOR)

            if code == 'y' or code == 'n':
                break
            else:
                print(RED_COLOR + '[!] Введеный неверный символ!')

def requirements():
    os.system("""
        pip3 install -U pyrogram tgcrypto configparser
        python3 -m pip install -U pyrogram tgcrypto configparser
        """)

try:
    if len(sys.argv) == 2:
        if sys.argv[1] == '-d':
            change_default_selection()
        elif sys.argv[1] == '-c':
            setup_content()
            change_content(ad_msg, ad_photo, ad_video)
        elif sys.argv[1] == '-i':
            requirements()
        else:
            print(RED_COLOR + '[!] Введеный неизвестный параметр!')
            sys.exit()
    else:
        setup_default()
        setup_content()
        save_default(api_id, api_hash, api_name)
        save_content(ad_msg, ad_photo, ad_video)

    with open('config.ini', 'w') as config_file:
        config.write(config_file)

except KeyboardInterrupt:
    sys.exit()