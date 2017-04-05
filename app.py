#!/usr/bin/env python

from flask import Flask

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/')
def default():
    #data = request.get_json()
    return 'Hello World!'

if __name__ == '__main__':

    app.run(host='0.0.0.0')
