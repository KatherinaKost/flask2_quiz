from flask import Flask, redirect, render_template, request, session, url_for, jsonify
from models1 import *
import os
from random import shuffle

BASE_DIR = os.path.dirname(__file__) #создали директорию где находится наш файл
DB_DIR = os.path.join(BASE_DIR, 'db') #добавляем в нашу директорию директорию с папкой db

if not os.path.exists(DB_DIR): #если нет папки создается автоматически
    os.makedirs(DB_DIR)

DB_PATH = os.path.join(DB_DIR, 'db_quiz.db')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SECRET_KEY'] = 'secretkeysecretkeysecretkey1212121'

db.init_app(app)  #связывается  приложение с бд

""" with app.app_context(): #запуск приложения
    add_data()          #в приложении выполняется функция по дбавлению данных в бд с gunicorn получится конфликт и поэтому это нужно запустить отдельно
     """
    



@app.route('/', methods=['POST', 'GET'])
def view_quiz():
    if request.method == 'GET':
        session['quiz.id'] = -1
        quizes = Quiz.query.all() #при методе ГЕТ просто показываем весь список квизов
        return render_template('start.html', quizes=quizes) 
    
    session['quiz.id'] = request.form.get('quiz')  #эта сессия для конкретного квиза с вопросами который выбрал пользователь
    session['question_n'] = 0
    session['question_id'] = 0
    session['right_answers'] = 0
    return redirect(url_for('viev_question'))

@app.route('/question/', methods=['POST', 'GET'])
def viev_question():
    if not session['quiz.id'] or session['quiz.id'] == -1:
        return redirect(url_for('view_quiz'))


    if request.method == 'POST': # если пост значит ответ на вопрос 
        question = Question.query.filter_by(id=session['question_id'])[0]  #так как в GET мы запомнили айди вопроса теперь для формы мы запоминаем именно этот вопрос, на который дается ответ
        if question.answer == request.form.get('answer'):   #в чтмл прописать answer #именно этот вопрос по айди мы просматриваем ответ
            session['right_answers'] += 1
        session['question_n'] += 1

    quiz = Quiz.query.filter_by(id=session['quiz.id']).all()  #выгружаем снова наш квиз
    if int(session['question_n']) >= len(quiz[0].question):          #quiz[0]  это сам ОБЪЕКТ так как у нас получается список ОБЪЕКТОВ
        session['quiz_id'] = -1 # чтобы больше не работала страница question
        return redirect(url_for('viev_result'))
    
    else:#тут надо показать вопросы поэтому метод GET
        question = quiz[0].question[session['question_n']] #мы отбираем первый вопрос с индексом 0 из нашего списка вопросов выбранного квиза
        session['question_id'] = question.id #запоминаем вопрос который показываем по айди
        answers = [question.answer, question.wrong1, question.wrong2]
        shuffle(answers)
        return render_template('question.html', question=question, answer=answers) #прописать чтмл

@app.route('/result/')
def viev_result():
    return render_template('result.html', right=session['right_answers'], total=session['question_n']) #прописать чтмл

@app.route('/login/', methods=['POST', 'GET'])
def login():
    users = User.query.all()   #тут на ГЕТ просто показываем пользователей

    if request.method == 'POST': #тут уже ПОСТ пользователь выбирает себя
        user_id = request.form.get('user_id')   #берем юзера по айди который пришел по форме
        if user_id and user_id.isdigit():  #проверяем ли все пришло верно, если нет обратно на логин перекинем, номер придет в ЧТМЛ через user.id
            user = User.query.get(int(user_id)) #берем из бд нашего польз по айди
            if user:
                session['user_id'] = user.id  #если все ок открываем сессию под нашего пользователя
                return redirect(url_for('view_quiz'))  #тут перенаправить на страницу с выбором квиза, где появится уже меню
            
    return render_template('login.html', users=users)

@app.route('/my_quizes/')
def my_quizes():
    if 'user_id' not in session:      #проверка вошел ли юзер
        return redirect(url_for('login'))
    
    quizes = Quiz.query.filter_by(user_id=session['user_id']).all() #отображаем все квизы которые есть у юзера
    return render_template('my_quizes.html', quizes=quizes)

@app.route('/edit_quiz/<int:quiz_id>/', methods=['POST', 'GET'])
def edit_quiz(quiz_id):
    if 'user_id' not in session:      #проверка вошел ли юзер
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    quiz = Quiz.query.get(quiz_id)

    if not quiz or quiz.user_id != user_id:  #проверка есть ли квиз и совпали ли айдишники
        return redirect(url_for('my_quizes'))
    
    if request.method == 'POST':
        quiz.name = request.form.get("quiz_name", quiz.name).strip()

        kept_question = []

        for question in quiz.question:
            if request.form.get(f'keep_{question.id}') == 'on':
                kept_question.append(question.id)      #добавляем сохраненные галочкой вопросы (их айди) которые не нужно удалять

        for question in quiz.question:
            if question.id in kept_question:
                question.question = request.form.get(f'q_{question.id}_text', question.question).strip()
                question.answer = request.form.get(f'q_{question.id}_ans', question.answer).strip()
                question.wrong1 = request.form.get(f'q_{question.id}_w1', question.wrong1).strip()
                question.wrong2 = request.form.get(f'q_{question.id}_w2', question.wrong2).strip()
            else:
                db.session.delete(question) #удаляем вопросы

        new_q_text = request.form.get('new_question_text', '').strip()
        new_q_ans = request.form.get('new_question_ans', '').strip()
        new_q_w1 = request.form.get('new_question_w1', '').strip()
        new_q_w2 = request.form.get('new_question_w2', '').strip()

        if all([new_q_text, new_q_ans, new_q_w1, new_q_w2]):
            new_question = Question(
                question=new_q_text,
                answer=new_q_ans,
                wrong1=new_q_w1,
                wrong2=new_q_w2
            )
            db.session.add(new_question)
            quiz.question.append(new_question)  # связываем с квизом

        db.session.commit() # Сохраняем изменения
        return redirect(url_for('edit_quiz', quiz_id=quiz_id))  
    return render_template('edit_quiz.html', quiz=quiz) # GET: показываем форму редактирования

@app.route('/create_quiz/', methods=['POST', 'GET'])
def create_quiz():
    if 'user_id' not in session:      #проверка вошел ли юзер
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        user_id = session['user_id']
        user = User.query.get(session['user_id'])
        new_quiz = Quiz(name,user)

        db.session.add(new_quiz)
        db.session.commit()

        return redirect(url_for('edit_quiz', quiz_id=new_quiz.id))
    return render_template('create_quiz.html')

@app.route('/delete-quiz/<int:quiz_id>/', methods=['POST'])
def delete_quiz(quiz_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    quiz = Quiz.query.get(quiz_id)
    if not quiz or quiz.user_id != session['user_id']:
        return redirect(url_for('my_quizes'))
    
    db.session.delete(quiz)  # cascade='all, delete-orphan' удалит и вопросы
    db.session.commit()
    return redirect(url_for('my_quizes'))

@app.route('/logout/')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('view_quiz'))


@app.errorhandler(404)
def page_not_found(e):
    #snip
    return '<h1 style="color:red; text-align:center"> Упс..... </h1>'





#app.run(debug=True, host='0.0.0.0', port=5555)
    

