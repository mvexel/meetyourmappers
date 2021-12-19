#!/bin/sh
gunicorn --workers 3 --bind unix:/home/mvexel/meetyourmappers/meetyourmappers.sock -m 777 meetyourmappers:app
