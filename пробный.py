from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Указываем путь к базе данных SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Отключаем предупреждения

# Создаем объект базы данных
db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.String, default=False)

    def __repr__(self):
        return f"<Task {self.title}>"

# Создаем таблицу в базе данных
with app.app_context():
    db.create_all()




@app.route('/')
@app.route('/tasks')
def get_tasks():
    tasks = Task.query.all()  # Получаем все записи из таблицы
    return {task.id: {"title": task.title, "completed": task.completed} for task in tasks}

@app.route('/add/<title>/<completed>')
def add_task(title, completed):
    new_task = Task(title=title, completed=completed)  # Создаем объект задачи
    db.session.add(new_task)  # Добавляем в сессию
    db.session.commit()  # Сохраняем в базе
    return f"Task '{title}' added!"


# Запуск сервера
if __name__ == "__main__":
    app.run(debug=True)