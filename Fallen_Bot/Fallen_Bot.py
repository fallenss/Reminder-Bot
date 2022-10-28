#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ast import Or
from pickle import FALSE, TRUE
import sqlite3
import telebot;
import datetime
from datetime import date, datetime, tzinfo, time
from datetime import timedelta, timezone
import requests
from time import sleep
from sqlite3 import Error
import configparser
import sched, time
import random
import re 


name = '';
surname = '';
age = 0;
config = configparser.ConfigParser()
config.read("config.ini")
bot = telebot.TeleBot(config['Telegram']['token']);
conn = sqlite3.connect('db/database.db', check_same_thread=False)
cursor = conn.cursor()
s = sched.scheduler(time.time, time.sleep)


class UTC3(tzinfo):
    """tzinfo derived concrete class named "+0530" with offset of 19800"""
    # can be configured here
    _offset = timedelta(hours=3)
    _dst = timedelta(0)
    _name = "МСК"
    def utcoffset(self, dt):
        return self.__class__._offset
    def dst(self, dt):
        return self.__class__._dst
    def tzname(self, dt):
        return self.__class__._name
tz = UTC3()

def db_new_user(user_id: int, user_name: str, user_surname: str, username: str):
    cursor.execute('INSERT INTO Users (user_id, user_name, user_surname, username) VALUES (?, ?, ?, ?)', (user_id, user_name, user_surname, username))
    conn.commit()


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

def delete_record():
    try:
        today = datetime.now(tz).strftime("%Y-%m-%d")
        sql_delete_query = f"""DELETE from Events where Events.time < '{today}'"""
        cursor.execute(sql_delete_query)
        conn.commit()
    except Error as e:
        print(f"The error '{e}' occurred")

     

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.from_user.id, 'Чего тебе?');


def chek_all(message):
      try:
          event_all = "Я напомню тебе о:\n"
          us_id = message.from_user.id
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
              event_all += event[3]+' '+event[2]+'\n'
          if event_all !="Я напомню тебе о:\n":
              bot.send_message(message.from_user.id, event_all)
          else: bot.send_message(message.from_user.id, "Не о чем мне тебе напоминать.")

      except :
          bot.send_message(message.from_user.id, '*звуки смэрти*')



@bot.message_handler(commands=['remi'])
def help_message(message):
    chek_all(message)


@bot.message_handler(commands=['help'])
def help_message(message):
	bot.send_message(message.from_user.id, '/reg - Регистрация пользователя\n/remi - Запланированные напоминания\nПримеры напоминаний:\nв 12 покурить\nзавтра в 14 помацать\n25 в 10:20 возьми еды');
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

chekin = False

def chek(message):
    global chekin
    if chekin==False:
        chekin = True
        def chek_in():
                s.enter(60, 1, chek_in)
                try:
                    us_id = message.from_user.id
                    today = datetime.now(tz).strftime("%Y-%m-%d")
                    totime = datetime.now(tz).strftime("%H:%M")
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
                    delete_record()
                except :
                    bot.send_message(message.from_user.id, '*звуки смэрти*')
        chek_in()
        s.run()
        


@bot.message_handler(content_types=['text', 'document', 'audio'])
def get_text_messages(message):


    if message.text.lower() == 'мяу':
        bot.send_message(message.from_user.id, "Хуль ты мяучешь?")
    else:
        try:
            done = False
            us_id = message.from_user.id
            mes = message.text
            
            match = re.search(r'\d\d/\d\d/\d\d \d\d:\d\d', mes)
            if match and done == False:
                mes = mes.split()
                time_str = mes[0]+' '+mes[1]
                mes[0]='';mes[1]=''
                mes = " ".join(mes)
                mes = mes.strip()
                ev_time = datetime.strptime(time_str, "%d/%m/%y %H:%M")
                db_event(user_id=us_id, event=mes, time=ev_time)
                done = True

            match = re.search(r'[З,з]автра [в,В] \d\d:\d\d', mes)
            if match and done == False:
                mes = mes.split()
                time_str = mes[2]
                mes[0]='';mes[1]='';mes[2]=''
                mes = " ".join(mes)
                mes = mes.strip()
                today = datetime.now(tz)
                today = today + timedelta(days=1)
                ev_time = today.strftime("%d/%m/%y")+' '+time_str
                ev_time = datetime.strptime(ev_time, "%d/%m/%y %H:%M")
                db_event(user_id=us_id, event=mes, time=ev_time)
                done = True
                
            match = re.search(r'[в,В] \d\d:\d\d', mes)
            if match and done == False:
                mes = mes.split()
                time_str = mes[1]
                mes[0]='';mes[1]=''
                mes = " ".join(mes)
                mes = mes.strip()
                today = datetime.now(tz).strftime("%d/%m/%y")
                ev_time = today+' '+time_str
                ev_time = datetime.strptime(ev_time, "%d/%m/%y %H:%M")
                db_event(user_id=us_id, event=mes, time=ev_time)
                done = True

            match = re.search(r'[З,з]автра [в,В] \d\d', mes)
            if match and done == False:
                mes = mes.split()
                time_str = mes[2]
                mes[0]='';mes[1]='';mes[2]=''
                mes = " ".join(mes)
                mes = mes.strip()
                today = datetime.now(tz)
                today = today + timedelta(days=1)
                ev_time = today.strftime("%d/%m/%y")+' '+time_str+':00'
                ev_time = datetime.strptime(ev_time, "%d/%m/%y %H:%M")
                db_event(user_id=us_id, event=mes, time=ev_time)
                done = True
                
            match = re.search(r'[в,В] \d\d', mes)
            if match and done == False:
                mes = mes.split()
                time_str = mes[1]
                mes[0]='';mes[1]=''
                mes = " ".join(mes)
                mes = mes.strip()
                today = datetime.now(tz).strftime("%d/%m/%y")
                ev_time = today+' '+time_str+':00'
                ev_time = datetime.strptime(ev_time, "%d/%m/%y %H:%M")
                db_event(user_id=us_id, event=mes, time=ev_time)
                done = True

            match = re.search(r'[З,з]автра [в,В] \d:\d\d', mes)
            if match and done == False:
                mes = mes.split()
                time_str = mes[2]
                mes[0]='';mes[1]='';mes[2]=''
                mes = " ".join(mes)
                mes = mes.strip()
                today = datetime.now(tz)
                today = today + timedelta(days=1)
                ev_time = today.strftime("%d/%m/%y")+' '+time_str
                ev_time = datetime.strptime(ev_time, "%d/%m/%y %H:%M")
                db_event(user_id=us_id, event=mes, time=ev_time)
                done = True

            match = re.search(r'[в,В] \d:\d\d', mes)
            if match and done == False:
                mes = mes.split()
                time_str = mes[1]
                mes[0]='';mes[1]=''
                mes = " ".join(mes)
                mes = mes.strip()
                today = datetime.now(tz).strftime("%d/%m/%y")
                ev_time = today+' '+time_str
                ev_time = datetime.strptime(ev_time, "%d/%m/%y %H:%M")
                db_event(user_id=us_id, event=mes, time=ev_time)
                done = True  

            match = re.search(r'[З,з]автра [в,В] \d', mes)
            if match and done == False:
                mes = mes.split()
                time_str = mes[2]
                mes[0]='';mes[1]='';mes[2]=''
                mes = " ".join(mes)
                mes = mes.strip()
                today = datetime.now(tz)
                today = today + timedelta(days=1)
                ev_time = today.strftime("%d/%m/%y")+' '+time_str+':00'
                ev_time = datetime.strptime(ev_time, "%d/%m/%y %H:%M")
                db_event(user_id=us_id, event=mes, time=ev_time)
                done = True
                
            match = re.search(r'[в,В] \d', mes)
            if match and done == False:
                mes = mes.split()
                time_str = mes[1]
                mes[0]='';mes[1]=''
                mes = " ".join(mes)
                mes = mes.strip()
                today = datetime.now(tz).strftime("%d/%m/%y")
                ev_time = today+' '+time_str+':00'
                ev_time = datetime.strptime(ev_time, "%d/%m/%y %H:%M")
                db_event(user_id=us_id, event=mes, time=ev_time)
                done = True   
                
            if done == False: 
                raise Exception('Unsupported or invalid request')    
                
            answer = random.randint(0, 6)
            match answer:
                case 0:
                    bot.send_message(message.from_user.id, f"Хм, окей.\nЯ напомню тебе в {time_str} о {mes}.")
                case 1:
                    bot.send_message(message.from_user.id, f"А? Ладно, но сильно не обольщайся.\nВ {time_str} я скажу чтобы ты {mes}.")
                case 2:
                    bot.send_message(message.from_user.id, f"В {time_str} так в {time_str}, без проблем.")
                case 3:
                    bot.send_message(message.from_user.id, f"Я не буду служить тебе вечно, но о {mes} скажу, так и быть.")
                case 4:
                    bot.send_message(message.from_user.id, f"Серьёзно? В {time_str}?\nТы хоть представляешь сколько...\nЛадно, забей... Всё будет.")
                case 5:
                    bot.send_message(message.from_user.id, f"Если бы мне платили каждый раз, когда я напоминал о том что нужно {mes}, меня здесь уже давно бы не было...\nОкей.")
                case 6:
                    bot.send_message(message.from_user.id, f"Во сколько? в {time_str}?\nНу, может быть и не забуду, гха-хаха...")
                case _:
                    bot.send_message(message.from_user.id, "СМЭРТ")            


            chek(message)
 

        except :
            answer = random.randint(0, 5)
            match answer:
                case 0:
                    bot.send_message(message.from_user.id, "Ты меня раздражаешь...\n/help")
                case 1:
                    bot.send_message(message.from_user.id, "Что, писать разучился?\n/help")
                case 2:
                    bot.send_message(message.from_user.id, "Фиктивный, моё терпение не безгранично.\n/help")
                case 3:
                    bot.send_message(message.from_user.id, "Думаешь это смешно?\n/help")
                case 4:
                    bot.send_message(message.from_user.id, "Слабоумие не лечится, да?\n/help")
                case 5:
                    today = datetime.now(tz).strftime("%d/%m/%y %H:%M")
                    bot.send_message(message.from_user.id, f'Нормально напиши, как в /help')   
                case _:
                    bot.send_message(message.from_user.id, "СМЭРТ")
            





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
