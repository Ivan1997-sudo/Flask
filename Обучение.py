from flask import Flask

# Создаем объект приложения Flask
app = Flask(__name__)

# Определяем маршрут и привязываем его к функции
@app.route('/')
def hello():
    return "Hello, Flask11111!"

# Запуск приложения
if __name__ == "__main__":
    app.run(debug=True)