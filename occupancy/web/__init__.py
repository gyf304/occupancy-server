"""THE occupancy flask app as a whole"""
from flask import Flask

app = Flask(__name__)

import occupancy.web.api
import occupancy.web.rpc
