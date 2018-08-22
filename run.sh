#!/bin/bash
mkdir -p /var/log/meetyourmappers
touch /var/log/meetyourmappers/requests.log
python3 -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=meetyourmappers
export FLASK_DEBUG=true
flask run
