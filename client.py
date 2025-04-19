import psutil
import requests
import time
import hashlib

SERVER_URL = 'https://lookup.zhiyuhub.top/api'

# 认证方式选择
print("请选择认证方式:")
print("1. 使用API密钥")
print("2. 使用用户名密码")
auth_choice = input("请输入选项(1/2): ")

if auth_choice == '1':
    API_KEY = input('请输入API密钥: ')
    auth_data = {'api_key': API_KEY}
elif auth_choice == '2':
    username = input('请输入用户名: ')
    password = input('请输入密码: ')
    # 对密码进行SHA256哈希
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    auth_data = {'username': username, 'password': hashed_password}
else:
    print("无效选项，默认使用API密钥")
    API_KEY = input('请输入API密钥: ')
    auth_data = {'api_key': API_KEY}

while True:
    # 获取当前运行的程序
    processes = [p.name() for p in psutil.process_iter()]
    # 获取电池信息
    battery = psutil.sensors_battery()
    battery_percent = battery.percent if battery else None
    # 获取CPU使用率
    cpu_percent = psutil.cpu_percent(interval=1)
    # 获取内存使用情况
    memory_usage = psutil.virtual_memory().percent
    # 获取网络状态
    net_io = psutil.net_io_counters()
    network_stats = {
        'bytes_sent': net_io.bytes_sent,
        'bytes_recv': net_io.bytes_recv
    }
    # 准备数据
    data = {
        'processes': processes,
        'battery_percent': battery_percent,
        'cpu_percent': cpu_percent,
        'memory_usage': memory_usage,
        'network_stats': network_stats,
        **auth_data
    }
    # 发送POST请求
    try:
        requests.post(SERVER_URL, json=data)
    except Exception as e:
        print(f'Error sending data: {e}')
    # 等待15秒
    time.sleep(15)