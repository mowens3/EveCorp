import os
import http.server
import socketserver
import start_app
import start_bot

from http import HTTPStatus
from commissar.app import app



start_app.app.start()
start_bot.bot.start()
