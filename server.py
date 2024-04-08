import os
import http.server
import socketserver
import start_app
import start_bot
from commissar.app import app
from commissar import ConfigLoader

from http import HTTPStatus
from commissar.app import app
cfg = ConfigLoader().config


start_app.app.start()
start_bot.bot.start()
