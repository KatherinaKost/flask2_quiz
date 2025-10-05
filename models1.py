from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):  #db.Model для наследования создавать таблицы,преобразовывать объекты в строки БД и обратно,строить SQL-запросы за кулисами
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    quizes = db.relationship('Quiz',
                              backref='user', 
                              cascade = 'all, delete, delete-orphan',
                              lazy='select') 
    def __repr__(self):
        return f'{self.id} - {self.name}'


class Quiz(db.Model): #конструктор квиза
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name:str, user:User): #создали свой конструктор
        super().__init__()
        self.name = name
        self.user = user  #если бы не указали, что юзер относится к классу юзер то бд просила бы айди юзера (связь по айди)
    def __repr__(self):
        return f'{self.id} - {self.name}'
    

quiz_question = db.Table('quiz_question',
                         db.Column('quiz_id', db.Integer, db.ForeignKey('quiz.id'), primary_key=True),
                         db.Column('question_id', db.Integer, db.ForeignKey('question.id'), primary_key=True),
                         )  #таблица для связей многое ко многому


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    answer = db.Column(db.String(100), nullable=False)
    wrong1 = db.Column(db.String(100), nullable=False)
    wrong2 = db.Column(db.String(100), nullable=False)
    quiz = db.relationship('Quiz', secondary=quiz_question, backref='question') #secondary=quiz_question """ связь через вторичную таблицу """

    def __init__(self, question, answer, wrong1, wrong2):
        super().__init__()
        self.question = question
        self.answer = answer
        self.wrong1 = wrong1
        self.wrong2 = wrong2
    def __repr__(self):
        return f'{self.id} - {self.question}'


def add_data():
    db.drop_all()  #удаляет все данные, для того чтобы лишнего ничего не накапливалось
    db.create_all()

    user1 = User(name='User1')
    user2 = User(name='User2')

    quizes = [
        Quiz('quiz1', user1),
        Quiz('quiz2', user2),
        Quiz('quiz3', user1),
    ]
    
    questions = [
        Question('Скульптура «Медный всадник» посвящена', 'Петру великому', 'Александру III', 'Николаю II'),
        Question('Как называется «детектор лжи»?', 'полиграф', 'полиндром', 'поликарп'),
        Question('Сколько жизней у кошек', '9', '10', '8'),
        Question('Орхидея - национальный цветок какой страны?', 'Тайланд', 'Китай', 'Вьетнам'),
        Question('Петух одним из национальных символов какой страны является?', 'Франция', 'Португалия', 'Испания'),
        Question('Для хранения чего пираты используют бочки', 'Рома', 'Пива', 'Мяса'),
        Question('С дневнегреческого "синий камень" переводится как:', 'Сапфир', 'Луна', 'Звезда'),
        Question('Каллисто и ИО спутники:', 'Юпитера', 'Сатурна', 'Марса'),
        Question('Чернобуркой называют вид', 'Лисы', 'Волка', 'Кошачьих'),
    ]

    quizes[0].question.append(questions[1])
    quizes[0].question.append(questions[3])
    quizes[0].question.append(questions[5])
    quizes[0].question.append(questions[2])
    quizes[0].question.append(questions[7])

    quizes[1].question.append(questions[6])
    quizes[1].question.append(questions[4])
    quizes[1].question.append(questions[0])
    quizes[1].question.append(questions[2])
    quizes[1].question.append(questions[1])

    quizes[2].question.append(questions[8])
    quizes[2].question.append(questions[2])
    quizes[2].question.append(questions[5])
    quizes[2].question.append(questions[7])
    quizes[2].question.append(questions[0])

    db.session.add_all(quizes) #буфер между твоим кодом и настоящей базой данных.подготовка к сохранению
    db.session.commit() #сохранение
    


