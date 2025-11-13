from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

# Инициализация базы данных
db = SQLAlchemy()

# Таблица пользователей
class User(UserMixin, db.Model):
    __tablename__ = "Пользователи"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15))
    email = db.Column(db.String(100))
    phone = db.Column(db.String)
    password_hash = db.Column(db.String(256))

# Таблица всех книг. -добавить имеющееся количество?
class Book(db.Model):
    __tablename__ = "Список книг"
    id = db.Column(db.Integer, primary_key=True)
    title_book = db.Column(db.String, nullable=False)
    author = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(20), nullable=False)
    #cover = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer)
    year = db.Column(db.Integer)

# Таблица отзывов
class Review(db.Model):
    __tablename__ = "Отзывы"
    id = db.Column(db.Integer, primary_key=True)
    review = db.Column(db.String, nullable=False)
    title_book = db.Column(db.String, nullable=False)
    username = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100))
    estimation = db.Column(db.Integer, nullable=False)

# Элемент корзины - Представляет собой книгу, которую пользователь добавил в корзину перед оформлением заказа.
# Это "корзина" перед покупкой, временная, для выбора товаров.
# Создается и удаляется при добавлении и удалении товаров из корзины.
class CartItem(db.Model):
    __tablename__ = "Корзина"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100))
    title_book = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# Заказ — запись о конкретном заказ
class Order(db.Model):
    __tablename__ = "Заказ"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100))
    date = db.Column(db.String, nullable=False)
    recipients_name = db.Column(db.String(20), nullable=False)
    recipients_phone = db.Column(db.String, nullable=False)
    recipients_email = db.Column(db.String(100), nullable=False)
    payment_method = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    method_receipt = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

# Элемент заказа - Представляет книгу, которая уже была куплена в рамках выполненного заказа.
# В одном заказе может быть несколько товаров.
# Создается при оформлении заказа и остается в базе для исторических целей.
class OrderItem(db.Model):
    __tablename__ = "Элемент заказа"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, nullable=False)
    title_book = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)

