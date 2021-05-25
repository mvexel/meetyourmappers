#!/bin/bash
touch log/requests.log
export FLASK_APP=meetyourmappers
export FLASK_DEBUG=true
flask run
