from distutils.log import error
import re
import eventlet
import json
from functools import wraps
from flask import Flask, render_template, request, session, flash, redirect
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap

eventlet.monkey_patch()

app = Flask(__name__)
app.secret_key = 'chave_secreta_123'
app.config['SECRET'] = 'my secret key'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = '192.168.1.113'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False
app.config['MQTT_CLEAN_SESSION'] = True

mqtt = Mqtt(app)
socketio = SocketIO(app)
bootstrap = Bootstrap(app)

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'username' in session:
            return test(*args, **kwargs)
        else:
            app.logger.info("Unauthorized access attempted!")
            return redirect('/login')
    return wrap


@app.route('/admin')
@login_required
def admin():
    return "<h1>Admin Page</h1>"


@app.route('/login', methods=['GET'])
def login():
    return """
    <h1>Login</h1>
    <form method='post' action='/login'>
        <input type='text' name='username' /><br />
        <input type='password' name='password' /><br />
        <input type='submit' />
    </form>
    """


@app.route('/login', methods=['POST'])
def login_submit():
    username = request.form["username"]
    password = request.form["password"]

    if password != "senha":
        return "Failed!"
    else:
        session['username'] = "admin"
        return render_template('index.html')

@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/sala_teste')
@login_required
def temp():
    return render_template('sala_teste.html')

@app.route('/teste')
@login_required
def teste():
    return render_template('teste.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')


#@socketio.on('publish')
#def handle_publish(json_str):
#    data = json.loads(json_str)
#    mqtt.publish(data['topic'], data['message'])

@socketio.on('subscribe')
def handle_subscribe(json_str):
    data = json.loads(json_str)
    mqtt.subscribe(data['topic'])

@socketio.on('unsubscribe_all')
def handle_unsubscribe_all():
    mqtt.unsubscribe_all()

#@mqtt.on_topic('temp')
#def handle_temp(client, user, message):
#    pld=message.payload.decode()
#    socketio.emit('mqtt_message_temp', pld=pld)

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    socketio.emit('mqtt_message', data=data)


@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)


if __name__ == '__main__':
    # important: Do not use reloader because this will create two Flask instances.
    # Flask-MQTT only supports running with one instance
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=False)

