from pyrogram import Client, compose
from pyrogram.types import InputPhoneContact
import random
import tempfile
from pyrogram.errors import PeerIdInvalid
from pyrogram.errors import RPCError
import sys
import time
import configparser
from threading import Thread

RED_COLOR = "\033[1;31m"
GREEN_COLOR = "\033[1;32m"
BLUE_COLOR = "\033[1;36m"
PURPLE_COLOR = "\033[1;35m"

api_id = []
api_hash = []
api_names = []
threads = []
ad_msg = None
ad_photo = None
ad_video = None
app = None 


def read_config():
    global api_id, api_hash, ad_msg, ad_photo, ad_video, app, api_names
    config = configparser.ConfigParser()
    config.read('config.ini')

    api_names = config['DEFAULT']['api_names'].split(" ")
    for name in api_names:
        api_id.append(config['DEFAULT']['api_id_' + name])
        api_hash.append(config['DEFAULT']['api_hash_' + name]) 

        tmp_api_id = config['DEFAULT']['api_id_' + name]
        tmp_api_hash = config['DEFAULT']['api_hash_' + name]

        try :
            app = Client(name, api_id=tmp_api_id, api_hash=tmp_api_hash)
        except:
            print(RED_COLOR + "[-] Данные api_id и api_hash неверны!")
            sys.exit()

    ad_msg = config['CONTENT']['ad_msg']
    ad_photo = config['CONTENT']['ad_photo']
    ad_video = config['CONTENT']['ad_video']
    
    while True:
        code = input(PURPLE_COLOR + '[+] Информация для отправки:\n--> Текст сообщения:\n ' + ad_msg + "\n--> Файл фото: "
        + ad_photo + "\n--> Файл видео: " + ad_video + "\n\n--> Подтвердите информацию для отправки (y/n): " + BLUE_COLOR)
        
        if code == 'y':
            break;
        elif code == 'n': 
            print(RED_COLOR + '[!] Измените данные через setup!')
            sys.exit()
        else: print(RED_COLOR + '[!] Введеный неверный символ!')


def send_telegram_msg(phone_num, add_msg, ad_photo, ad_video, app, profile):
    temp_contact_name = tempfile.NamedTemporaryFile().name.split('\\')[-1]

    try:
        with app:
            app.import_contacts([InputPhoneContact(phone=phone_num, first_name=temp_contact_name)])
            app.send_message(phone_num, add_msg)
            if (ad_photo != ''):
                app.send_photo(phone_num, ad_photo)
            if (ad_video != ''):
                app.send_video(phone_num, ad_video)

    except PeerIdInvalid:
        return RED_COLOR + f"[-] Пользователь {phone_num} не найден!"

    except RPCError:
        return RED_COLOR + f"[-] Что-то странное произошло! ({phone_num})"

    return GREEN_COLOR + f"[{profile}] {phone_num} - Отправлено!"

def open_file(file_name):
    try:
        file = open(file_name, 'r')
        return file.readlines()
    except: 
        print(RED_COLOR + '[!] Файл по данному пути не существует!')
        sys.exit()

def easter_egg():
    if random.randint(0, 9) == 3:
        print(GREEN_COLOR + "\n[+] Ай ай ай, спамить не хорошо )")
    else : print(GREEN_COLOR + "\n[+] Запускаем отправку!")

def divide_chunks(list, n):
    for i in range(0, len(list), n):
        yield list[i:i + n]

def processing_send(phone_numbers, api_id, api_hash, api_names, profile_id):
    app = Client(api_names[profile_id], api_id[profile_id], api_hash[profile_id])

    counter = 1
    for phone_num in phone_numbers:
        if counter % 10 == 0:
            print(GREEN_COLOR + "\n[+] Пауза на 5 мин!")
            time.sleep(300)
            print(GREEN_COLOR + "\n[+] Бот возобновил работу!\n")
        
        print(send_telegram_msg(phone_num[:-1], ad_msg, ad_photo, ad_video, app, api_names[profile_id]))
        time.sleep(15)
        counter += 1

def single_mode(api_name, phone_numbers, api_id, api_hash, api_names):
    profile_id = -1
    for i in range(len(api_names)):
        if api_names[i] == api_name:
            profile_id = i
    if profile_id == -1:
        print(RED_COLOR + '[!] Введеный профиль не существует!')
        sys.exit()

    processing_send(phone_numbers, api_id, api_hash, api_names, profile_id)

def threading_mode(phone_numbers, api_id, api_hash, api_names):
    global threads

    profile_num = len(api_names)
    chunk_size = int(len(phone_numbers) / profile_num)

    phone_num_list = list(divide_chunks(phone_numbers, chunk_size))

    for i in range(profile_num):
        threads.append(Thread(target=processing_send, args=(phone_num_list[i], api_id, api_hash, api_names, i,)))
    
    for thread in threads:
        thread.start()    

def start_spamming(api_name, phone_numbers, api_id, api_hash, api_names):
    if api_name == None:
        threading_mode(phone_numbers, api_id, api_hash, api_names)
    else:
        single_mode(api_name, phone_numbers, api_id, api_hash, api_names)
        
    

try:
    if len(sys.argv) < 2: 
        print(RED_COLOR + '[!] Укажите параметры!')
        sys.exit()
    elif len(sys.argv) == 3: 
        api_name = sys.argv[2]
    elif len(sys.argv) == 2: 
        api_name = None
    
    phone_numbers = open_file(sys.argv[1])
    
    read_config()

    easter_egg()
    
    start_spamming(api_name, phone_numbers, api_id, api_hash, api_names)
    
except KeyboardInterrupt:
    sys.exit()