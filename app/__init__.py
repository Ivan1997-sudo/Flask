from flask import Flask

# Создаем объект приложения Flask
app = Flask(__name__)
from app import routes