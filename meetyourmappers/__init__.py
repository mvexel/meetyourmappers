'''Initialize flask app'''

#

from flask import Flask, session

app = Flask(__name__)
app.config.from_object("meetyourmappers.config")

import meetyourmappers.views  # pylint: disable=wrong-import-position,cyclic-import
