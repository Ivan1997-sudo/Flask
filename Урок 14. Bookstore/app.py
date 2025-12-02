from flask import Flask, request, flash, redirect, render_template, url_for, session
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import Email, EqualTo, InputRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
import datetime
import random
from models import User, Book, CartItem, Order, OrderItem, Review, db

app = Flask(__name__)

# Настройка базы данных SQLite
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация базы данных
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    email = StringField("Адрес электронной почты", validators=[InputRequired(), Email()])
    password = PasswordField("Пароль", validators=[InputRequired(), Length(min=8, max=36)])

class RegistrationForm(FlaskForm):
    username = StringField("Имя", validators=[InputRequired(), Length(min=2, max=100)])
    email = StringField("Адрес электронной почты", validators=[InputRequired(), Email()])
    phone = StringField("Номер телефона", validators=[InputRequired()])
    password = PasswordField("Пароль", validators=[InputRequired(), Length(min=8, max=36)])
    confirm_password = PasswordField( "Повторите пароль", validators=[InputRequired(), EqualTo("password")])

#Проверка для всех маршрутов, авторизован ли пользователь. Если да - меняем верхнюю панели и показываем количество книг в корзине
@app.context_processor
def inject_user_cart():
    if current_user.is_authenticated:
        cart_items = CartItem.query.filter_by(email=current_user.email).all()
        quantity = sum(item.quantity for item in cart_items)
        return {
            'name': current_user.username,
            'quantity_book': quantity,
            'cart_item': {x.title_book: x for x in cart_items}} #Определяем у авторизованного пользователя, какие книги есть в корзине
    else:
        return {
            'name': None,
            'quantity_book': 0,
            'cart_item': None}

#Главная страница книжного магазина
@app.route('/')
def main_page():
    books = Book.query.order_by(Book.rating.desc()).limit(10).all()
    books = {x.title_book: {'price': x.price, 'rating': x.rating} for x in books}
    return render_template('main_page.html', books=books)


#Каталог
@app.route('/catalog/<genre>')
def catalog(genre):
    books = Book.query.filter_by(genre=genre).all()
    books = {x.title_book: {'price': x.price, 'rating': x.rating} for x in books}
    return render_template('catalog.html', books=books, genre=genre)


#Страница книги
@app.route('/product/<title_book>', methods=['GET', 'POST'])
def product(title_book):
    if request.method == 'POST':
        review = request.form['review']
        estimation = request.form['estimation']
        #Проверка, оставлял ли пользователь уже отзыв на данную книгу
        if Review.query.filter_by(email=current_user.email, title_book=title_book).first() is None:
            new_review = Review(
                review=review,
                title_book=title_book,
                username=current_user.username,
                email=current_user.email,
                estimation = estimation)
            db.session.add(new_review)
        else:
            review_user = Review.query.filter_by(email=current_user.email, title_book=title_book).first()
            review_user.review = review
            review_user.estimation = estimation
        #Обновление среднего рейтинга книги
        review_sum = db.session.query(func.avg(Review.estimation)).filter_by(title_book=title_book).scalar()
        book = Book.query.filter_by(title_book=title_book).first()
        book.rating = round(review_sum, 1)
        db.session.commit()
        return redirect(request.referrer)
    #Определяем книгу, которую нужно открыть
    book = Book.query.filter_by(title_book=title_book).first()
    if book is None:
        flash(f"Книга с названием <{title_book}> не найдена", 'danger')
        return redirect(request.referrer)
    #Считываем отзывы на нее
    total_review = Review.query.filter_by(title_book=title_book).all()
    quantity_review = len(total_review)
    #Определяем наличие книги в корзине, если пользователь авторизован
    cart_item = None
    if current_user.is_authenticated:
        cart_item = CartItem.query.filter_by(email=current_user.email, title_book=title_book).first()
    return render_template('product.html', book=book, total_review=total_review, quantity_review=quantity_review, cart_item=cart_item)


#Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        #Путь для подтверждения номера телефона
        if  request.form.get('form_type') == "check":
            data = session.get('registration_data')
            if request.form.get('code') == session.get('secret_code'):
                user = User(
                    username=data['username'],
                    email=data['email'],
                    phone=data['phone'],
                    password_hash=data['password_hash'])
                db.session.add(user)
                db.session.commit()
                #Очистка сессии
                session.pop('registration_data', None)
                session.pop('secret_code', None)
                return redirect(url_for('login'))
            flash("Неправильный код подтверждения", 'danger')
            return render_template('register.html', show_modal=True, form=RegistrationForm(),
                entered_code=request.form.get('code'), secret_code = session.get('secret_code'), user = data)
    #Путь для регистрации пользователя
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Пользователь с данным email уже существует!", 'danger')
            return render_template('register.html', form=form)
        if User.query.filter_by(phone=form.phone.data).first():
            flash("Пользователь с данным номером телефона уже существует!", 'danger')
            return render_template('register.html', form=form)
        secret_code = "".join(map(str, [random.randint(0, 9) for i in range(4)]))
        # Сохранение данных в сессию
        session['registration_data'] = {
            'username': form.username.data,
            'email': form.email.data,
            'phone': form.phone.data,
            'password_hash': generate_password_hash(form.password.data)}
        session['secret_code'] = secret_code
        return render_template('register.html', show_modal=True, form=form, secret_code=secret_code)
    elif form.errors:
        #flash(form.errors, category='danger')
        if 'email' in form.errors:
            flash("Ошибка ввода email!", 'danger')
        if 'confirm_password' in form.errors:
            flash("Пароли не совпадают!", 'danger')
    return render_template('register.html', form=form)


#Вход
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #Путь для подтверждения номера телефона
        if  request.form.get('form_type') == "check":
            user = User.query.filter_by(email=session['email']).first()
            if request.form.get('code') == session.get('secret_code'):
                login_user(user)
                session.pop('email', None)
                session.pop('secret_code', None)
                return redirect(url_for('main_page'))
            flash("Неправильный код подтверждения", 'danger')
            return render_template('login.html', show_modal=True, form=RegistrationForm(),
                entered_code=request.form.get('code'), secret_code=session.get('secret_code'), user=user)
    #Путь для входа
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            secret_code = "".join(map(str, [random.randint(0, 9) for i in range(4)]))
            session['email'] = form.email.data
            session['secret_code'] = secret_code
            return render_template('login.html', show_modal=True, form=form, secret_code=secret_code, user=user)
        flash('Неверное имя пользователя или пароль', 'danger')
    elif form.errors:
        flash(form.errors, category='danger')
    return render_template('login.html', form=form)


#Выход
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


#Корзина
@app.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    title_book = request.args.get('title_book')
    action = request.args.get('action')
    if request.method == 'POST':
        #Определяем, есть ли книга, которую пользователь хочет положить в корзину, уже в ней
        order = CartItem.query.filter_by(email=current_user.email, title_book=title_book).first()
        if order and action == "+1":
            order.quantity += 1
        if order and action == "-1":
            order.quantity -= 1
        if order and (order.quantity == 0 or action == "Удалить"):
            CartItem.query.filter_by(email=current_user.email, title_book=title_book).delete()
        if not order:
            order = CartItem(
                email=current_user.email,
                title_book=title_book,
                quantity=1)
            db.session.add(order)
        db.session.commit()
        return redirect(request.referrer)
    #Определяем книги в корзине пользователя
    cart_item = CartItem.query.filter_by(email=current_user.email).all()
    cart_item = {x.title_book : x.quantity for x in cart_item} #Словарь название книги: количество в корзине
    total_book = 0
    total_summ = 0
    book_user = {} #Словарь название книги: количество, цена и автор
    for i in cart_item:
        book = Book.query.filter_by(title_book = i).first()
        book_user[i] = {'quantity': cart_item[i], 'price': book.price, 'author': book.author}
        total_book += cart_item[i]
        total_summ += book.price * cart_item[i]
    return render_template('cart.html', book_user=book_user, total_summ=total_summ, total_book=total_book)


#Оформление заказа
@app.route('/making', methods=['GET', 'POST'])
@login_required
def making():
    if request.method == 'POST':
        # Проверяем, что пользователь указал адрес
        if request.form["Способ получения"] == "Самовывоз":
            if not request.form.get("pickup-address"):
                flash("Выберите магазин для самовывоза", 'danger')
                return redirect(url_for('making'))
        if request.form["Способ получения"] == "Доставка":
            if request.form["delivery-address"].strip() == "":
                flash("Введите адрес доставки", 'danger')
                return redirect(url_for('making'))
        # Создаем заказ в таблице Order
        order = Order(
            email = current_user.email,
            date = datetime.datetime.now().date().strftime("%d-%m-%Y"),
            recipients_name = request.form['name'],
            recipients_phone=request.form['number'],
            recipients_email = request.form['email'],
            payment_method = request.form['payment_method'],
            status = "Заказ выполняется",
            method_receipt = request.form['Способ получения'],
            address = request.form['pickup-address'] if request.form["Способ получения"] == "Самовывоз" else request.form["delivery-address"])
        db.session.add(order)
        db.session.commit()
        order_id = order.id
        # Определяем книги в корзине пользователя и добавляем в OrderItem
        item = CartItem.query.filter_by(email=current_user.email).all()
        for i in item:
            book = Book.query.filter_by(title_book=i.title_book).first()
            order_item = OrderItem (
            order_id = order_id,
            title_book = i.title_book,
            quantity = i.quantity,
            price = book.price)
            db.session.add(order_item)
        # Очищаем корзину
        CartItem.query.filter_by(email=current_user.email).delete()
        db.session.commit()
        return redirect(url_for('orders'))
    #Определяем книги в корзине пользователя
    cart_item = CartItem.query.filter_by(email=current_user.email).all()
    cart_item = {x.title_book : x.quantity for x in cart_item} #Словарь название книги: количество в корзине
    total_book = 0
    total_summ = 0
    book_user = {} #Словарь название книги: количество и цена
    info_user = {"Имя": current_user.username, "Номер": current_user.phone, "email": current_user.email}
    for i in cart_item:
        book = Book.query.filter_by(title_book = i).first()
        book_user[i] = {'quantity': cart_item[i], 'price': book.price, 'author': book.author}
        total_book += cart_item[i]
        total_summ += book.price * cart_item[i]
    if total_book < 1:
        return redirect(request.referrer)
    return render_template('making.html', book_user=book_user, total_summ=total_summ, total_book=total_book, info_user=info_user)


#История заказов
@app.route('/orders', methods=['GET', 'POST'])
@login_required
def orders():
    # Все заказы пользователя
    all_orders = Order.query.filter_by(email = current_user.email).all()
    # Словарь id заказа: элементы заказы
    id_order_item = {}
    # Словарь id заказа: цена
    price_item = {}
    for order in all_orders:
        order_item = OrderItem.query.filter_by(order_id = order.id).all()
        id_order_item[order.id] = order_item
        price_item[order.id] = sum(i.price for i in order_item)
    return render_template('orders.html', all_orders=all_orders, id_order_item=id_order_item, price_item=price_item)


#Запуск сервера
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)