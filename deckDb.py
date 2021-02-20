import random


class DeckDb:
    cards = []

    def __init__(self, db, user_id):
        self.db = db
        self.user_id = user_id

    def create_table(self):#создаем таблицу, если ее нет
        cursor = self.db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS deck (
                              "id"    INTEGER PRIMARY KEY AUTOINCREMENT,
                              "ranks"  INTEGER,
                              "kinds"  VARCHAR,
                              "user_id"  INTEGER,
                              "status"  INTEGER DEFAULT (0)  
                        )''')
        self.db.commit()

    def makeKids(self):
        self.kinds = ['H', 'C', 'D', 'S']

    def makeRanks(self):
        self.ranks = ['2', '3', '4', '6', '7', '8', '9', '10', '11']

    def gen_cards(self):  # генерируем колоду
        self.makeKids()
        self.makeRanks()
        for i in self.ranks:
            for j in self.kinds:
                self.cards.append([i, j])
        return self.cards
        # self.cards = self.cards.append([i, j] for i in self.ranks for j in self.kinds)

    def shuf(self):  # перемешиваем колоду
        random.shuffle(self.cards)

    def get_card(self):  # берем одну карту
        return self.cards.pop()

    def makeDbDeck(self):  # заполняем таблицу колодой и user_id
        self.gen_cards()
        self.shuf()

        while len(self.cards) != 0:
            current_card = self.get_card()
            cursor = self.db.cursor()
            cursor.execute("INSERT INTO deck (ranks, kinds, user_id) VALUES (?, ?, ?)",
                           (current_card[0], current_card[1], self.user_id))
            self.db.commit()

    def takeDbCard(self, user_type):  # помечаем вытянутую карту и выдаем пользователю
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM deck WHERE status = 0 AND user_id = ? LIMIT 1", [self.user_id])
        res = cursor.fetchone()
        r = res[0]
        cursor.execute("UPDATE deck SET status = ? WHERE id = ? ", (user_type, r))  # удалила фром после аптдейт
        self.db.commit()
        return res

    def sum(self, user_type):  # сумма карт
        cursor = self.db.cursor()
        cursor.execute("SELECT SUM(ranks) AS sm FROM deck WHERE status = ? AND user_id = ? LIMIT 1",
                       [user_type, self.user_id])  # изменила звёздочку на ранкс
        summa = cursor.fetchone()
        return summa

    def botCards(self, user_type):  # список карт бота
        cursor = self.db.cursor()
        cursor.execute('''SELECT ranks,
                                 kinds
                          FROM deck 
                          WHERE status = 2 AND user_id = ? ''', [self.user_id])
        list_bot_cards = cursor.fetchall()
        return list_bot_cards
        print(list_bot_cards)

    def destroyDeck(self):  # clear a table
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM deck WHERE user_id = ? ", [self.user_id])
        self.db.commit()

    #
