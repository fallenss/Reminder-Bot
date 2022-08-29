from ast import Or;
from asyncio.windows_events import NULL;
import sqlite3;
import telebot;
import datetime
from datetime import date, datetime
import re
import requests
from telebot import types;
from threading import Thread
from time import sleep
from sqlite3 import Error


name = '';
surname = '';
age = 0;
bot = telebot.TeleBot('5677279515:AAFlofhF6P30B7oxYjncTNG7l6pNElmx8tY');
conn = sqlite3.connect('db/database.db', check_same_thread=False)
cursor = conn.cursor()



def db_new_user(user_id: int, user_name: str, user_surname: str, username: str):
    try:
        cursor.execute('INSERT INTO Users (user_id, user_name, user_surname, username) VALUES (?, ?, ?, ?)', (user_id, user_name, user_surname, username))
        conn.commit()
    except Error as e:
        print(f"The error '{e}' occurred")

def db_event(user_id: int, event: str, time: datetime):
    try:
        cursor.execute('INSERT INTO Events (user_id, event, time) VALUES (?, ?, ?)', (user_id, event, time))
        conn.commit()
    except Error as e:
        print(f"The error '{e}' occurred")

def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.from_user.id, 'Чего тебе?');
    def chek_in():
        try:
            while True:
                us_id = message.from_user.id
                today = datetime.now().strftime("%Y-%m-%d")
                totime = datetime.now().strftime("%H:%M")
                select_event = f"""
            SELECT *
            FROM
              Events
            WHERE
              Events.user_id = {us_id}
            ORDER BY
              time
            """
                events = execute_read_query(conn, select_event)
                for event in events:
                    ev_time = datetime.strptime(event[3], "%Y-%m-%d %H:%M:%S")
                    ev_time = ev_time.date().strftime("%Y-%m-%d")
                    if ev_time == today:
                        ev_time = datetime.strptime(event[3], "%Y-%m-%d %H:%M:%S")
                        ev_time = ev_time.time().strftime("%H:%M")
                        if ev_time == totime:
                            bot.send_message(message.from_user.id, event[2])
                sleep(60)
        except :
            bot.send_message(message.from_user.id, '*звуки смэрти*')
    th = Thread(target=chek_in)
    th.start()



	


@bot.message_handler(commands=['help'])
def help_message(message):
	bot.send_message(message.from_user.id, '/reg - Регистрация пользователя\nПримеры напоминаний (не рабочие, пока):\nв 12 покурить\nзавтра в 14 помацать\n25 в 10:20 возьми еды');
@bot.message_handler(commands=['reg'])
def reg_message(message):
    try:
        us_id = message.from_user.id
        us_name = message.from_user.first_name
        us_sname = message.from_user.last_name
        username = message.from_user.username
        db_new_user(user_id=us_id, user_name=us_name, user_surname=us_sname,username=username)
        bot.send_message(message.from_user.id, 'Так, ну вроде я тебя запомнил.')
    except :
        bot.send_message(message.from_user.id, 'Хм, походу ты в БД уже есть.')
    






#def get_age(message):
#    global age;
#    while age == 0: #проверяем что возраст изменился
#        try:
#             age = int(message.text) #проверяем, что возраст введен корректно
#        except Exception:
#             bot.send_message(message.from_user.id, 'Цифрами, пожалуйста');
#             bot.register_next_step_handler(message, get_age);
#             return 0
#    keyboard = types.InlineKeyboardMarkup(); #наша клавиатура
#    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes'); #кнопка «Да»
#    keyboard.add(key_yes); #добавляем кнопку в клавиатуру
#    key_no= types.InlineKeyboardButton(text='Нет', callback_data='no');
#    keyboard.add(key_no);
#    question = 'Тебе '+str(age)+' лет, тебя зовут '+name+' '+surname+'?';
#    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


@bot.message_handler(content_types=['text', 'document', 'audio'])
def get_text_messages(message):
    #type_event = 0
    if message.text.lower() == 'привет':
        bot.send_message(message.from_user.id, "Ты меня раздражаешь...")
    else:
        try:
            us_id = message.from_user.id
            mes = message.text
            mes = mes.split()
            time_str = mes[0]+' '+mes[1]
            mes[0]='';mes[1]=''
            mes = " ".join(mes)
            mes = mes.strip()
            ev_time = datetime.strptime(time_str, "%d/%m/%y %H:%M")
            db_event(user_id=us_id, event=mes, time=ev_time)
            bot.send_message(message.from_user.id, f"Хм, окей.\nЯ напомню тебе в {time_str} о {mes}")
        except :
            bot.send_message(message.from_user.id, f'Нормально напиши, как в примере:\n{datetime.now().strftime("%d/%m/%y %H:%M")} сходить покурить')





    #match type_event:
    #    case "200":
    #        print("OK")
    #        do_something_good()
    #    case "404":
    #        print("Not Found")
    #        do_something_bad()
    #    case "418":
    #        print("I'm a teapot")
    #        make_coffee()
    #    case 0:
            
        

#@bot.callback_query_handler(lambda call : call.data)
#def callback_worker(call):
#        if call.data == "yes": #call.data это callback_data, которую мы указали при объявлении кнопки
#            bot.send_message(call.message.chat.id, 'Запомню : )');
#        elif call.data == "no":
#            bot.send_message(call.message.chat.id, 'Ну давай по новой... /reg');




bot.polling(none_stop=True)
