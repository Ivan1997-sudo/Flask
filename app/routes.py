from app import app

# Определяем маршрут и привязываем его к функции
@app.route('/')
def h():
    return "Hello!"

@app.route('/hello')
def hello():
    return "Hello, world!"

@app.route('/info')
def info():
    return "This is an informational page"

@app.route('/calc/<x>/<y>')
def calc(x, y):
    try:
        x = int(x)
        y = int(y)
    except ValueError:
        return "Нужно указать числа"
    return f"The sum of {x} and {y} is {int(x) + int(y)}"

@app.route('/reverse/<text>')
def reverse(text):
    if len(text) > 1:
        return text[::-1]
    return "Текст должен быть длиннее"

@app.route('/user/<name>/<int:age>')
def user(name, age):
    if int(age) >= 0:
        return f"Hello, {name}. You are {age} years old."
    return "Ваш возраст отрицателен, рекомендуем обратиться к врачу"