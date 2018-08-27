activate_this = '/home/meetyourmappers/meetyourmappers/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from meetyourmappers import app as application
