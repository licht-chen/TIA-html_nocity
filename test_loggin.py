import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify
from time import strftime
import traceback

app = Flask(__name__)

@app.route("/")
def get_index():
    return "Welcome to the Python Flask's Index! "

@app.route("/hello")
def get_hello():
    return "Hello! "

@app.route("/json")
def get_json():
    data = {"Name":"Ivan Leon","Age":"27","Books":"[Crime and Punishment, The Gambler, Twenty Thousand Leagues Under The Sea]"}
    return jsonify(data_WRONG) # INTENTIONAL ERROR FOR TRACEBACK EVENT

@app.after_request
def after_request(response):
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    logger.error('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status)
    return response

@app.errorhandler(Exception)
def exceptions(e):
    tb = traceback.format_exc()
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    logger.error('%s %s %s %s %s 5xx INTERNAL SERVER ERROR\n%s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, tb)
    return e.status_code


if __name__ == '__main__':
    handler = RotatingFileHandler('app.log', maxBytes=100000, backupCount=3)
    logger = logging.getLogger('tdm')
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)
    app.run()