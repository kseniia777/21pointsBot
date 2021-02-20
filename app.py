import telebot
from telebot import types
import sqlite3

import config
from deckDb import DeckDb

# подключаемся к базе
db = sqlite3.connect('test_db.sqlite', check_same_thread=False)

# подключаем
bot = telebot.TeleBot(config.TOKEN)


# Ответ на команду старт
@bot.message_handler(commands=['start'])
def welcome(message):
    # keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("🎲 Играть в Очко: 2️⃣1️⃣")
    item2 = types.KeyboardButton("🎯Цель игры🎯")
    markup.add(item1, item2)  # добавляем кнопку на клавиатуре
    bot.send_message(message.chat.id,
                     "{0.first_name}, приветсвую тебя!\nЯ - {1.first_name}.\nСыграй в игру и набери ровно 2️⃣1️⃣ очко.\nЖелаю удачи! ".format(
                         message.from_user, bot.get_me( )), reply_markup=markup)


# Кнопки
@bot.message_handler(content_types=['text'])
def first_keyboard(message):
    if message.chat.type == 'private':
        if message.text == '🎯Цель игры🎯':
            bot.send_message(message.chat.id,
                             'Цель игры - набрать в сумме 21 очко.🤗\nКарты J, D, K - дают 2, 3, 4 очка соответсвнно;\nA - 11 очков;\n6, 7, 8, 9, 10 - дают количество очков, равное рангу.\nЖелаю удачи😉')
        elif message.text == '🎲 Играть в Очко: 2️⃣1️⃣':
            # удаление
            create = DeckDb(db, message.chat.id)
            create.create_table( )
            dest = DeckDb(db, message.chat.id)
            dest.destroyDeck()

            # выводим кнопки
            markup = types.InlineKeyboardMarkup(row_width=2)
            item3 = types.InlineKeyboardButton("Беру карту", callback_data='eshe')
            item4 = types.InlineKeyboardButton("Хватит", callback_data='stop')
            markup.add(item3, item4)
            # создаем объек колоды
            deck = DeckDb(db, message.chat.id)
            deck.makeDbDeck( )
            bot.send_message(message.chat.id, 'Выбирай:', reply_markup=markup)
            # добавляем в таблицу айди пользавателя.

        else:
            bot.send_message(message.chat.id, 'Я не знаю, что ответить')


# раздача
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'eshe':

                # передаём тип пользователя
                deck = DeckDb(db, call.message.chat.id)
                deck1 = deck.takeDbCard(1)
                rank = deck1[1]
                kind = deck1[2]
                if kind == 'S':
                    kind = '♠'
                elif kind == 'H':
                    kind = '♥'
                elif kind == 'D':
                    kind = '♦'
                elif kind == 'C':
                    kind = '♣'
                if rank == 2:
                    rank = 'J'
                elif rank == 3:
                    rank = 'D'
                elif rank == 4:
                    rank = 'K'
                elif rank == 11:
                    rank = 'A'

                summa = DeckDb(db, call.message.chat.id)
                user_summa = summa.sum(1)
                s = (user_summa[0])
                # список карт бота
                k = DeckDb(db, call.message.chat.id)
                k1 = k.botCards(2)

                markup = types.InlineKeyboardMarkup(row_width=2)
                item2 = types.InlineKeyboardButton("Беру карту", callback_data='eshe')
                item3 = types.InlineKeyboardButton("Хватит", callback_data='stop')
                markup.add(item2, item3)

                bot.send_message(call.message.chat.id,
                                 'Тебе попалась карта %s %s! \nВсего очков - %d.' % (rank, kind, s),
                                 reply_markup=markup)



            elif call.data == 'stop':

                # сумма у бота
                summa_b = DeckDb(db, call.message.chat.id)
                bot_summa = summa_b.sum(2)
                s_b = int(bot_summa[0] or 0)
                list_ranks = []
                while s_b < 17:
                    deckBt = DeckDb(db, call.message.chat.id)
                    deckBot2 = deckBt.takeDbCard(2)
                    list_ranks.append(deckBot2[1])
                    s_b = sum(list_ranks)

                # сумма у польователя
                summa_u = DeckDb(db, call.message.chat.id)
                user_summa = summa_u.sum(1)
                s = (user_summa[0])
                # список карт бота
                list_bot = DeckDb(db, call.message.chat.id)
                lis = list_bot.botCards(2)
                l = []
                for i in lis:
                    b = list(i)
                    for j in b:
                        if b[1] == 'H':
                            b[1] = '♥'
                        elif b[1] == 'D':
                            b[1] = '♦'
                        elif b[1] == 'S':
                            b[1] = '♠'
                        elif b[1] == 'C':
                            b[1] = '♣'
                        elif b[0] == 2:
                            b[0] = 'J'
                        elif b[0] == 3:
                            b[0] = 'D'
                        elif b[0] == 4:
                            b[0] = 'K'
                        elif b[0] == 11:
                            b[0] = 'A'
                    l.append(b)
                l2 = str(l).strip('[]')
                liststr = ('[' + l2 + ']')

                bot.send_message(call.message.chat.id,
                                 'У тебя %d очков и ты закончил игру. \nА бот набрал %d. \nОн вытащил - \n%s ' % (
                                     s, s_b, liststr))
                # сравниваем количество очков
                if s == s_b:
                    bot.send_message(call.message.chat.id,
                                     'У вас ничья! \nВот это совпадение😉.')
                elif s == 21:
                    bot.send_message(call.message.chat.id,
                                     'Поздравляю🥳!\nТы набрал 2️⃣1️⃣ и победил в этой игре!')
                elif s_b == 21:
                    bot.send_message(call.message.chat.id,
                                     'Бот набрал 2️⃣1️⃣ и победил в этой игре! \nА тебе обязательно повезёт в следующий раз😜!')
                elif s > 21 and s_b > 21:
                    bot.send_message(call.message.chat.id,
                                     'И ты и Бот проиграли в этой игре, набрав больше 2️⃣1️⃣. \nПовезёт в следующий раз😜!')
                elif s < 21 and s_b < 21:
                    if (21 - s) > (21 - s_b):
                        bot.send_message(call.message.chat.id,
                                         'Ты проиграл в этой игре, \nБот был ближе к 2️⃣1️⃣. \nПовезёт в следующий раз😜!')
                    else:
                        bot.send_message(call.message.chat.id,
                                         'Поздравляю🥳!\nТы был ближе к 2️⃣1️⃣ и победил в этой игре!')
                elif s < 21 and s_b > 21:
                    bot.send_message(call.message.chat.id,
                                     'Поздравляю🥳!\nТы победил в этой игре! \nА вот у Бота перебор😓')
                else:
                    bot.send_message(call.message.chat.id,
                                     'В этой игре победил Бот! \nА вот у тебя перебор😓. \nПовезёт в следующий раз😜!')
                    # удаление
                dest = DeckDb(db, call.message.chat.id)
                dest.destroyDeck()

                bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                          text="Игра окончена!")

    except Exception as e:
        print(repr(e))


bot.polling(none_stop=True)
