from flask import Flask,render_template#,send_file
from threading import Thread

app = Flask('')

@app.route('/')
def main():
    return render_template('index.html')

def run():
    app.run(host='0.0.0.0', port=8080)

def server():
    server = Thread(target=run)
    server.start()