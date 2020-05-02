import telebot
import config
from telebot import types
import os
from string import Template
import mysql.connector
import random

bot = telebot.TeleBot(config.TOKEN)
adm = config.admin_id
db = mysql.connector.connect(
  host = "localhost",
  user = "root",
  passwd = "root",
  port = "3306",
  database='jaks'
)
cursor = db.cursor()

chars = '+-/*!&$#?=@<>abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
#print(bot.get_chat('@jakskarel').id)
#-1001278959677
num = int(1)
strs = int(28)

#cursor.execute('CREATE DATABASE jaks')

#способ ввода переменных, для увелечения производительности, объявление переменной юзер для дальнейшей работы

#cursor.execute('CREATE TABLE users (fullname VARCHAR(255), phone VARCHAR(255))')

#cursor.execute('ALTER TABLE users ADD COLUMN (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT UNIQUE)')
#sql = 'INSERT INTO users (fullname, phone, user_id) VALUES (%s, %s, %s)'
#val = ('Александр Безручко Александрович','89771794246', 1)
#cursor.execute(sql, val)


user_data = {}
class User:
    def __init__(self, fullname):
        self.fullname = fullname
        self.phone = ''
# /reg
@bot.message_handler(commands=["start"])
def process_city_step(message):
    user_id = message.from_user.id
    if message.chat.id == 713832075:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.row('Статистика','Пользователи')
        markup.row('Объявление')
        markup.row('Редактирование')
        bot.send_message(message.chat.id, "Привет админ", reply_markup=markup)
    elif not(message.chat.id == 713832075):
        bot.send_message(message.chat.id, "Добро пожаловать в ххх  " 
        + message.from_user.first_name 
        +" зарегестрируйтесь пожалуйста")
        # удалить старую клавиатуру
        markup = types.ReplyKeyboardRemove(selective=False)

        msg = bot.send_message(message.chat.id, 'Фамилия Имя Отчество')
        bot.register_next_step_handler(msg, process_fullname_step)

def process_fullname_step(message):
    try:
        user_id = message.from_user.id
        user_data[user_id] = User(message.text)

        msg = bot.send_message(message.chat.id, 'Ваш номер телефона')
        bot.register_next_step_handler(msg, process_phone_step)

    except Exception as e:
        bot.reply_to(message, 'ooops!!')

def process_phone_step(message):
    try:
        int(message.text)

        user_id = message.from_user.id
        user = user_data[user_id]
        user.phone = message.text

        
        sql = 'INSERT INTO users (fullname, phone, user_id) VALUES (%s, %s, %s)'
        val = (user.fullname, user.phone, user_id)
        cursor.execute(sql, val)
        db.commit()

        bot.send_message(-1001278959677, 'ФИО: ' 
        + user.fullname
        + '; Номер телефона: '
        + str(user.phone)
        +'; id '
        + str(user_id))
        bot.send_message(message.chat.id, 'Вы успешно зарегестрировались, напишите /help')
    except Exception as e:
        msg = bot.reply_to(message, 'Ошибка! Вы уже зарегестрированны. Наша компания может вам перезвонить.')
        keyboard = types.InlineKeyboardMarkup(); #наша клавиатура
        key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes'); #кнопка «Да»
        keyboard.add(key_yes); #добавляем кнопку в клавиатуру
        key_no = types.InlineKeyboardButton(text='Нет', callback_data='no');
        keyboard.add(key_no);
        question = str(user.phone)+' Перезвонить на этот номер? ';
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes": #call.data это callback_data, которую мы указали при объявлении кнопки
        ...
        bot.send_message(call.message.chat.id, 'Хорошо, ваше сообщение получено, скоро перезвоним, ожидайте');
    elif call.data == "no":
        ...
        msg = bot.send_message(call.message.chat.id, 'Укажите новый номер');
        bot.register_next_step_handler(msg, process_reg_phone_step)
def process_reg_phone_step(message):
    int(message.text)
    user_id = message.from_user.id
    phone = message.text

    sql = ("UPDATE users SET phone = %s \
                    WHERE user_id = %s")
    val = (phone, user_id)   
    cursor.execute(sql, val) 
    db.commit()
    bot.send_message(message.chat.id, 'Вы успешно сменили номер телефона')

@bot.message_handler(commands=['help'])
def send_welcome(message):
    if message.chat.id == 713832075:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.row('Статистика','Пользователи')
        markup.row('Объявление')
        markup.row('Редактирование')
        bot.send_message(message.chat.id, message.from_user.first_name +" админ", reply_markup=markup)
    elif not(message.chat.id == 713832075):
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.row('Услуги','Перезвонить')
        markup.row('О компании', 'Получить промо')
        bot.send_message(message.chat.id, "Профиль " 
            + message.from_user.first_name
            +" Ваш номер ",  reply_markup=markup)

# произвольный текст
@bot.message_handler(content_types=["text"])
def send_help(message):
    try:
        user_id = message.from_user.id
        if message.chat.id == 713832075:
            if message.text.lower() == 'пользователи':
                sql = ('SELECT * FROM users')
                cursor.execute(sql)
                
                result = cursor.fetchall()
                for x in result:
                    bot.send_message(message.chat.id, x[2] 
                    + ' Номер: ' 
                    + x[3])
                
            elif message.text.lower() == 'редактирование':
                msg = bot.send_message(message.chat.id, 'Введите id пользователя')
                bot.register_next_step_handler(msg, id_user)
                
    except Exception as e:        
        if not(message.chat.id == 713832075):
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.row('Услуги','Перезвонить')
            markup.row('О компании')
            if message.text.lower() == 'услуги':
                bot.send_message(message.chat.id, 'Тут будет либо ссылка на сайт с описанием услуг, либо само описание, либо и то и другое');
            elif message.text.lower() == 'о компании':
                bot.send_message(message.chat.id, 'Тут будет либо ссылка на сайт с описанием вашей компании, либо само описание, либо и то и другое')
            elif message.text.lower() == 'перезвонить':
                msg = bot.send_message(message.from_user.id, 'Повторите свой номер телефона пожалуйста')
                bot.register_next_step_handler(msg, phone)
            elif message.text.lower() == 'получить промо':
                try:  
                    user_id = message.from_user.id
                    user_data[user_id] = User(message.text)
                    for x in range( num ):
                        w = ''
                    for i in range(strs):
                        w += random.choice( chars )
            
                    sql = 'INSERT INTO promo (promocode, user_id) VALUES (%s, %s)'
                    val = ( w, user_id)
                    cursor.execute(sql, val)
                    db.commit()
                    bot.send_message(message.chat.id, w + ' помните, промо можно получать раз в 24 часа')
                except Exception as e:
                    bot.send_message(message.chat.id, 'вы уже получали промо, дождитесь пока пройдут сутки')
            else:
                bot.send_message(message.chat.id, 'Регистрация - /reg\nПомощь - /help')
def id_user(message):
    user_id = message.text
    
    # удалить старую клавиатуру
    markup = types.ReplyKeyboardRemove(selective=False)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.row('Номер','ФИО')
    markup.row('Редоктировать о компании')
    bot.send_message(message.chat.id, 'Выберете что будете редактировать', reply_markup=markup)
def phone(message):
    int(message.text)
    user_id = message.from_user.id
    phone = message.text
    
    keyboard = types.InlineKeyboardMarkup(); #наша клавиатура
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes'); #кнопка «Да»
    keyboard.add(key_yes); #добавляем кнопку в клавиатуру
    key_no= types.InlineKeyboardButton(text='Нет', callback_data='no');
    keyboard.add(key_no);
    question = str(phone)+' Перезвонить на этот номер? ';
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
          
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes": #call.data это callback_data, которую мы указали при объявлении кнопки
        ...
        bot.send_message(call.message.chat.id, 'Хорошо, ваше сообщение получено, скоро перезвоним, ожидайте');
    elif call.data == "no":
        ...
        msg = bot.send_message(call.message.chat.id, 'Укажите новый номер');
        bot.register_next_step_handler(msg, process_reg_phone_step)

    
    

# произвольное фото
@bot.message_handler(content_types=["photo"])
def send_help_text(message):
    bot.send_message(message.chat.id, 'Напишите текст')

# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()

if __name__ == '__main__':
    bot.polling(none_stop=True)