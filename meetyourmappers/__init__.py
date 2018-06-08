from flask import Flask, session
app = Flask(__name__)
app.secret_key = 'owfoiwnef aiefliuaehlifamewlfihaeilw '
import meetyourmappers.views
