from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Настройка базы данных SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация базы данных
db = SQLAlchemy(app)

class SecretAgency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code_name = db.Column(db.String(15), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(20), nullable=False)
    access_level = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f"<SecretAgency {self.id}>"

# Создаем таблицу в базе данных
with app.app_context():
    db.create_all()

#Список всех агентов
@app.route("/")
def full_list():
    agents = SecretAgency.query.all()
    return render_template('SecretAgency.html', agents=agents)

#Заполни анкету для нового шпиона
@app.route("/add", methods=['GET', 'POST'])
def add_agent():
    if request.method == 'POST':
        code_name = request.form['code_name']
        number = request.form['number']
        email = request.form['email']
        access_level = request.form['access_level']
        if code_name.strip():  # Проверяем, что строка не пустая
            new_agent = SecretAgency(code_name=code_name, number=number, email=email, access_level=access_level)
            db.session.add(new_agent)
            db.session.commit()
        return redirect(url_for('full_list'))
    return render_template('add_agent.html')

#Все данные о конкретном агенте!!!!!!!!!!
@app.route("/agent/<id>")
def agent(id):
    agent = SecretAgency.query.get_or_404(id)
    return render_template('info_agent.html', agent=agent)

#Обновление информации
@app.route("/edit/<id>", methods=['GET', 'POST'])
def edit(id):
    agent_id = SecretAgency.query.get_or_404(id)
    if request.method == 'POST':
        code_name = request.form['code_name']
        number = request.form['number']
        email = request.form['email']
        access_level = request.form['access_level']
        if code_name.strip():  # Проверяем, что строка не пустая
            agent_id.code_name = code_name  # Изменяем кодовое имя
            agent_id.number = number
            agent_id.email = email
            agent_id.access_level = access_level
            db.session.commit()  # Сохраняем изменения
        return redirect(url_for('full_list'))
    return render_template('edit_agent.html', agent = agent_id)

#Удаление досье
@app.route("/delete/<id>")
def delete(id):
    agent = SecretAgency.query.get_or_404(id)  # Получаем задачу по ID
    db.session.delete(agent)  # Удаляем
    db.session.commit()  # Подтверждаем изменения
    return redirect(url_for('full_list'))

# Запуск сервера
if __name__ == "__main__":
    app.run(debug=True)





