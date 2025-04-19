from flask import Flask, request, jsonify, render_template, redirect
from datetime import datetime
import uuid
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)

import json
import os

# 会话数据文件路径
SESSIONS_FILE = 'sessions.json'

# 从文件加载会话数据
def load_sessions():
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, 'r') as f:
            return json.load(f)
    return {}

# 保存会话数据到文件
def save_sessions(sessions):
    with open(SESSIONS_FILE, 'w') as f:
        json.dump(sessions, f)

# 存储会话数据
sessions = load_sessions()

@app.route('/api', methods=['POST'])
def api():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username not in sessions or not check_password_hash(sessions[username]['password'], password):
        return jsonify({'error': '无效的用户名或密码'}), 401
    
    # 更新会话数据
    sessions[username] = {
        'name': sessions[username].get('name', ''),
        'password': sessions[username]['password'],
        'processes': data.get('processes'),
        'battery_percent': data.get('battery_percent'),
        'cpu_percent': data.get('cpu_percent'),
        'memory_usage': data.get('memory_usage'),
        'network_stats': data.get('network_stats'),
        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    save_sessions(sessions)
    return jsonify({'status': 'success'})

@app.route('/')
def index():
    return render_template('index.html', sessions=sessions)

@app.route('/session/<api_key>')
def session(api_key):
    if api_key not in sessions:
        return '会话未找到', 404
    return render_template('session.html', session=sessions[api_key], datetime=datetime)

@app.route('/new_session', methods=['GET', 'POST'])
def new_session():
    if request.method == 'GET':
        return render_template('new_session.html')
    
    username = request.form.get('username')
    password = request.form.get('password')
    session_name = request.form.get('name')
    
    if not username or not password or not session_name:
        return render_template('new_session.html')
    
    if username in sessions:
        return render_template('new_session.html', error='用户名已存在')
    
    sessions[username] = {
        'name': session_name,
        'password': generate_password_hash(password),
        'processes': [],
        'battery_percent': 0,
        'cpu_percent': 0,
        'memory_usage': 0,
        'network_stats': {'bytes_sent': 0, 'bytes_recv': 0},
        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    save_sessions(sessions)
    return redirect(f'/congrats?key={username}')

@app.route('/congrats')
def congrats():
    api_key = request.args.get('key')
    if api_key not in sessions:
        return '会话未找到', 404
    return render_template('congrats.html', api_key=api_key, name=sessions[api_key]['name'])

if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
    #app.run(debug=True)