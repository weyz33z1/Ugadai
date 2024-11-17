from flask import Flask, render_template, request, url_for, redirect, session
import random
import math
from enum import Enum

app = Flask(__name__)
app.secret_key = "lol"

# Выносим сообщения для удобства
_messageInputRangeOut = "Пожалуйста, введите число в заданном диапазоне"
_messageWin = "Поздравляю, Вы угадали!"
_messageLose = "Игра окончена! Загаданным числом было "
_messageLessInputValue = "Увы, Вы не угадали, загаданное число больше "
_messageHighInputValue = "Увы, Вы не угадали, загаданное число меньше "

# Глобальные переменные для хранения состояния игры
min_number = 1
max_number = 100

# Создаем Enum для удобства
class State(Enum):
    inGame = 1
    inEnd = 2

# Наша страница с игрой
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "GET":

        # Если у нас нет игры, то создаем ее, поскольку это метод GET
        if isHaveGame():
            session["attempts"] = math.ceil(math.log2(max_number - min_number + 1))
            session["secret_number"] = random.randint(min_number, max_number)
            session["history"] = []
            session["state"] = State.inGame.value

        # Отрисовываем страницу
        return render_template("index.html", min_number = 0, max_number = 100, attempts = session["attempts"],
                               history = session["history"], state = session["state"])
    else:

        # Если у нас нет игры, то отрисовывем последние значения, поскольку это метод POST
        if isHaveGame():
            return render_template("index.html", min_number = 0, max_number = 100, attempts = session["attempts"],
                               history = session["history"], state = session["state"])

        # Берем с сессии все необходимые для работы значения
        guess = int(request.form["user_guess"])
        state = State(int(session["state"]))
        attempts = int(session["attempts"])
        secret_number = int(session["secret_number"])
        history = session["history"]
        message = ""

        # Проверяем введенное значение на :
        # - соответвие диапазону;
        # - совпадение загаданного числа (также изменяеям состояние игры на оконченную);
        # - введенное число больше загаданного;
        # - введенное число меньше загаданного
        if max_number < guess or guess < min_number:
            message = _messageInputRangeOut
        elif guess == secret_number:
            message = _messageWin
            attempts -= 1
            state = State.inEnd
        elif guess > secret_number:
            message = _messageHighInputValue + str(guess)
            attempts -= 1
        else:
            message = _messageLessInputValue + str(guess)
            attempts -= 1

        # Добовляем сообщение в историю
        history.insert(0, message)

        # Если закончились попытки и игра не выиграна, значит игра проиграна.
        # Добавляем в историю сообщение о поражении и изменяем состяние игра на оконченную
        if state == State.inGame and attempts <= 0:
            message = _messageLose + str(secret_number)
            history.insert(0, message)
            state = State.inEnd
        
        # Заносим все изменения в сессию
        session["attempts"] = attempts
        session["history"] = history
        session["state"] = state.value

        # рендерим страницу
        return render_template("index.html", min_number = 0, max_number = 100, attempts = attempts,
                               history = history, state = state.value)
        
# Страница перезагрузки игры
@app.route("/reset")
def resetGame():
    # Очищаем сессию и возвращается на страницу с игрой
    session.clear()
    return redirect("/")

# Страница ошибки 404
@app.errorhandler(404)
def error404(error):
    return render_template("error404.html")

# Проверка на наличие игры
def isHaveGame():
    cheack = session.get("state", None)

    return cheack is None or cheack == State.inEnd.value

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)