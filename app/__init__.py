from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
# для пожддержки кросс-доменности
CORS(app)

from app import views
