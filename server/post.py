import json
import queue
from unicodedata import name
from getGovPost import GetGovPost
import threading
import multiprocessing as mp
from multiprocessing import Process, Manager
from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS, cross_origin

# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')
app.config['JSON_AS_ASCII'] = False
CORS(app)

pName = 'getter'
q = mp.Queue()
lock = threading.Lock()
ggp = GetGovPost()

@app.route('/govpost')
def govpost():
    with open('./gov.txt') as f:
        json_data = json.load(f)
    return jsonify(json_data)

@app.route('/coronapost')
def post():
    with open('./corona.txt') as f:
        json_data = json.load(f)
    return jsonify(json_data)

@app.route('/refresh')
def refresh():
    global ggp
    if len(mp.active_children()) == 0:
        p = Process(target=ggp.process, args=(q,), name=pName)
        p.start()
        return 'process activated'
    else:
        i = 0
        while i < 100:
            if mp.active_children()[i].name == pName:
                break
            i += 1
        if i < len(mp.active_children()):
            # 살아있으면
            if mp.active_children()[i].is_alive():
                print('리프레시 하는 중')
                return 'refreshing...'
            # 죽었으면
            else:
                return 'refreshed!'
        

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)