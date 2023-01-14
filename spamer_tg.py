from pyrogram import Client, compose
from pyrogram.types import InputPhoneContact
import random
import tempfile
from pyrogram.errors import PeerIdInvalid
from pyrogram.errors import RPCError
import sys
import configparser
import asyncio

RED_COLOR = "\033[1;31m"
GREEN_COLOR = "\033[1;32m"
BLUE_COLOR = "\033[1;36m"
PURPLE_COLOR = "\033[1;35m"

api_id = []
api_hash = []
api_names = []
tasks = []
event_l = None
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
            print(RED_COLOR + f"[-] [{name}] Данные api_id и api_hash неверны или профиль заблокирован!")
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
    else: print(GREEN_COLOR + "\n[+] Запускаем отправку!")

def divide_chunks(list, n):
    for i in range(0, len(list), n):
        yield list[i:i + n]

async def send_telegram_msg(phone_numbers, api_id, api_hash, api_names, profile_id, stop_factor):
    app = Client(api_names[profile_id], api_id[profile_id], api_hash[profile_id])

    counter = 1
    for phone_num in phone_numbers:
        if counter % stop_factor == 0:
            print(GREEN_COLOR + f"\n[+] Пауза на 5 мин! {api_names[profile_id]}")
            await asyncio.sleep(300)
            print(GREEN_COLOR + f"\n[+] Бот возобновил работу! {api_names[profile_id]}\n")

        temp_contact_name = tempfile.NamedTemporaryFile().name.split('\\')[-1]

        try:
            async with app:
                await app.import_contacts([InputPhoneContact(phone=phone_num, first_name=temp_contact_name)])
                await app.send_message(phone_num, ad_msg)
                if (ad_photo != ''):
                    await app.send_photo(phone_num, ad_photo)
                if (ad_video != ''):
                    await app.send_video(phone_num, ad_video)

        except PeerIdInvalid:
            print(RED_COLOR + f"[{api_names[profile_id]}] [-] Пользователь {phone_num[:-1]} не найден!")
            continue

        except RPCError:
            print(RED_COLOR + f"[{api_names[profile_id]}] [-] Что-то странное произошло! ({phone_num[:-1]})")
            continue

        print(GREEN_COLOR + f"[{api_names[profile_id]}] {phone_num[:-1]} - Отправлено!")

        if (stop_factor > 5):
            await asyncio.sleep(10 + stop_factor - 4)
        else: 
            await asyncio.sleep(10 + stop_factor)
        counter += 1

def single_mode(api_name, phone_numbers, api_id, api_hash, api_names):
    profile_id = -1
    for i in range(len(api_names)):
        if api_names[i] == api_name:
            profile_id = i
    if profile_id == -1:
        print(RED_COLOR + '[!] Введеный профиль не существует!')
        sys.exit()

    asyncio.run(send_telegram_msg(phone_numbers, api_id, api_hash, api_names, profile_id, 10))

def threading_mode(phone_numbers, api_id, api_hash, api_names):
    global tasks

    profile_num = len(api_names)
    chunk_size = int(len(phone_numbers) / profile_num)

    phone_num_list = list(divide_chunks(phone_numbers, chunk_size))

    for i in range(profile_num):
        tasks.append(event_l.create_task(send_telegram_msg(phone_num_list[i], api_id, api_hash, api_names, i, 7 + i)))

    wait_tasks = asyncio.wait(tasks)
    event_l.run_until_complete(wait_tasks)
    event_l.close()

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
    
    event_l = asyncio.get_event_loop()
    start_spamming(api_name, phone_numbers, api_id, api_hash, api_names)
    
except KeyboardInterrupt:
    sys.exit()