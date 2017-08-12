"""THE occupancy flask app as a whole"""
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r'/api/*': {'origins': '*'}})

import occupancy.web.api
import occupancy.web.rpc
