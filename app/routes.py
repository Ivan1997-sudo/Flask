from flask import render_template, request, redirect, url_for
from app import app

# Определяем маршрут и привязываем его к функции
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

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