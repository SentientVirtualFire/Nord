from flask import Flask,render_template,redirect,send_file
from threading import Thread
from random import randrange

app = Flask('')

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def main():
    x=randrange(1,100)
    if x==7:
      return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return render_template('index.html')

@app.route("/favicon.ico")
def favicon():
  return send_file("favicon.ico")

'''
@app.route('/ping')
def ping():
  return('pong')
'''
def run():
    app.run(host='0.0.0.0', port=8080)

def server():
    server = Thread(target=run)
    server.start()
