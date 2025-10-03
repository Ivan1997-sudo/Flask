from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Настройка базы данных SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация базы данных
db = SQLAlchemy(app)

# Модель задачи (таблица Task)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f"<Task {self.title}>"

# Создаем таблицу в базе данных
with app.app_context():
    db.create_all()

### 📌 CRUD-МАРШРУТЫ

# 📌 Главная страница: список задач
@app.route('/')
@app.route('/tasks')
def get_tasks():
    tasks = Task.query.all()  # Получаем все задачи из базы
    return render_template('tasks.html', tasks=tasks)

# 📌 Добавление новой задачи
@app.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        if title.strip():  # Проверяем, что строка не пустая
            new_task = Task(title=title)
            db.session.add(new_task)
            db.session.commit()
        return redirect(url_for('get_tasks'))
    return render_template('add_task.html')

# 📌 Редактирование задачи
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    task = Task.query.get_or_404(id)  # Получаем задачу по ID
    if request.method == 'POST':
        new_title = request.form['title']
        if new_title.strip():
            task.title = new_title
            db.session.commit()
        return redirect(url_for('get_tasks'))
    return render_template('edit_task.html', task=task)

# 📌 Удаление задачи
@app.route('/delete/<int:id>')
def delete_task(id):
    task = Task.query.get_or_404(id)  # Получаем задачу по ID
    db.session.delete(task)  # Удаляем из базы
    db.session.commit()  # Подтверждаем изменения
    return redirect(url_for('get_tasks'))

# Запуск сервера
if __name__ == "__main__":
    app.run(debug=True)