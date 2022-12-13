from flask import Flask
from flask_restx import Api
from app.modules import HecsModel

app = Flask(__name__)
api = Api(app, title='Hecs Image Classification', default='Provide Endpoint', default_label='endpoints for classification brand/s')

from app import views