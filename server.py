from flask import Flask, request, jsonify, render_template, redirect
from datetime import datetime
import uuid
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
    api_key = data.get('api_key')
    if api_key not in sessions:
        return jsonify({'error': '无效的API密钥'}), 401
    
    # 更新会话数据
    sessions[api_key] = {
        'name': sessions[api_key].get('name', ''),
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
    
    session_name = request.form.get('name')
    if not session_name:
        return render_template('new_session.html')
    
    api_key = str(uuid.uuid4())
    sessions[api_key] = {
        'name': session_name,
        'processes': [],
        'battery_percent': 0,
        'cpu_percent': 0,
        'memory_usage': 0,
        'network_stats': {'bytes_sent': 0, 'bytes_recv': 0},
        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    save_sessions(sessions)
    return redirect(f'/congrats?key={api_key}')

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