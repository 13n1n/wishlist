from waitress import serve

from . import app

serve(app, port=8080)