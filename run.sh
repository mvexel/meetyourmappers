#!/bin/bash
mkdir -p log/meetyourmappers
touch log/meetyourmappers/requests.log
python3 -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=meetyourmappers
export FLASK_DEBUG=true
flask run
