import psutil
import requests
import time

SERVER_URL = 'https://lookup.zhiyuhub.top/api'
API_KEY = input('请输入API密钥: ')

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
        'api_key': API_KEY
    }
    # 发送POST请求
    try:
        requests.post(SERVER_URL, json=data)
    except Exception as e:
        print(f'Error sending data: {e}')
    # 等待15秒
    time.sleep(15)