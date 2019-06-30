from flask import Flask, session
import meetyourmappers

app = Flask(__name__)
app.config.from_object("meetyourmappers.config")

try:
    app.config.from_object("meetyourmappers.config_local")
except:
    pass

import meetyourmappers.views
