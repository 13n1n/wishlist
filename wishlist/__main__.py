from waitress import serve

from . import app, init


init()
serve(app, port=8080)