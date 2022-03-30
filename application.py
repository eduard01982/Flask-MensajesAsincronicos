
import psycopg2
# Start with a basic flask app webpage.
from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context
from random import random
from time import sleep
from threading import Thread, Event

__author__ = 'eduardo'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = False
app.config['HOST'] = '0.0.0.0'
app.config['PORT'] = 5000

#turn the flask app into a socketio app
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)

#random number Generator Thread
thread = Thread()
thread_stop_event = Event()


def listar():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT fecha,mensaje FROM prueba order by id desc limit 10;')
    m = cur.fetchall()
    #print(m);
    cur.close()
    conn.close()
    return m

def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='prueba',
                            user='postgres',
                            password='postgres')
    return conn

def randomNumberGeneratorInicial():
    print("Making random numbers")
    lista = listar()
    i = 0
    salida = ""
    while (i < len(lista)):
        for fila in lista[i]:
            #print(fila)
            salida += str(fila) + " "
        socketio.emit('newnumber', {'number': salida}, namespace='/test')
        salida = ""
        i += 1

def randomNumberGenerator():
    print("Making random numbers")
    listaoriginal = []
    lista = listar()
    i = 0
    salida = ""
    while not thread_stop_event.isSet():
        sleep(2)
        socketio.sleep(2)
        lista = listar()
        if (lista != listaoriginal):
            i = 0
            while (i < len(lista)):
                for fila in lista[i]:
                    #print(fila)
                    salida += str(fila) + " "
                socketio.emit('newnumber', {'number': salida}, namespace='/test')
                salida = ""
                i += 1
            listaoriginal = lista


@app.route('/')
def index():
    #only by sending this page first will the client be connected to the socketio instance
    return render_template('index.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global thread
    randomNumberGeneratorInicial()
    print('Client connected')

    #Start the random number generator thread only if the thread has not been started before.
    if not thread.isAlive():
        print("Starting Thread")
        thread = socketio.start_background_task(randomNumberGenerator)

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
   socketio.run(app,'0.0.0.0',5000)
