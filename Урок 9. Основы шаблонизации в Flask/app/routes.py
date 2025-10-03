from flask import render_template, request, redirect, url_for
from app import app
import datetime

# Определяем маршрут и привязываем его к функции
@app.route("/")
def home():
    now = datetime.datetime.now()
    weekday = {"Monday": "Понедельник", "Tuesday": "Вторник", "Wednesday": "Среда", "Thursday": "Четверг",
               "Friday": "Пятница", "Saturday": "Суббота", "Sunday": "Воскресенье"}
    month = {"January": "Январь", "Februar": "Февраль", "March": "Март", "April": "Апрель", "May": "Май",
    "June": "Июнь", "July": "Июль", "August": "Август", "September": "Сентябрь", "October": "Октябрь",
    "November": "Ноябрь", "December": "Декабрь"}
    return render_template("home.html", now = now, weekday = weekday[now.strftime('%A')],
                           month = month[now.strftime('%B')])

@app.route("/about")
def about():
    staff = [{"Должность": "Наблюдатель", "Обязанности": "Проследит, чтобы вы не изменили ничего критически важного для будущего всего мира"},
             {"Должность": "Охранник", "Обязанности": "Поможет избавиться от хранителей времени и других тварей"},
             {"Должность": "Навигатор","Обязанности":  "Рассчитает координаты переноса, чтобы вы не оказались в стене"}]
    return render_template("about.html", staff = staff )

@app.route("/contact")
def contact():
    rate = {"Базовый": {"Максимальное время скачка": "1 год", "Сложность изменения прошлого": "Незначительная"},
        "Продвинутый": {"Максимальное время скачка": "10 лет", "Сложность изменения прошлого": "умеренная"},
        "Премиум": {"Максимальное время скачка": "Любое", "Сложность изменения прошлого": "Тяжелое"}}
    return render_template("contact.html", rate=rate)

@app.route("/answer", methods=["POST", "GET"])
def answer():
    if request.method == "POST":
        name = request.form.get("name")  # Получаем имя из формы
        email = request.form.get("email")
        purpose = request.form.get("purpose")
        message = "Ваша заявка отправлена"
        return render_template("contact.html", message=message)
    else:
        return redirect(url_for("form"))  # Если запрос GET, возвращаем на форму