from flask import render_template, request, redirect, url_for
from app import app
import requests

# Определяем маршрут и привязываем его к функции

@app.route("/")
def form():
    return render_template("form.html")

@app.route("/submit", methods=["POST", "GET"])
def submit():
    if request.method == "POST":
        name = request.form.get("name")  # Получаем имя из формы
        email = request.form.get("email")  # Получаем email из формы

        color = request.form.get("color")
        name_color = None
        if color != "#000000":
            url = f"https://api.color.pizza/v1/?values={color[1:]}"
            response = requests.get(url)
            if response.status_code == 200:
                repos = response.json()
                name_color = repos['paletteTitle']
        else:
            color = None

        profession = request.form.get("profession")
        hobbies = request.form.getlist("hobbies")
        if len(hobbies) == 0:
            hobbies = False
        level = request.form.get("level")
        thing = request.form.get("thing")
        return render_template("result.html", name=name, email=email,
        color=color, name_color = name_color, profession=profession, hobbies=hobbies, level=level, thing=thing)
    else:
        return redirect(url_for("form"))  # Если запрос GET, возвращаем на форму