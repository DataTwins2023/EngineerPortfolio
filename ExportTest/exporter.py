from prometheus_client import start_http_server, Gauge
import psutil
import time
import traceback
import sys

# 定義 metrics
cpu_usage = Gauge('system_cpu_usage_percent', 'CPU 使用率 (%)')
mem_usage = Gauge('system_memory_usage_percent', '記憶體使用率 (%)')
disk_usage = Gauge('system_disk_usage_percent', '磁碟使用率 (%)', ['mountpoint'])

def collect_metrics():
    try:
        while True:
            # CPU 使用率
            cpu = psutil.cpu_percent(interval=1)
            cpu_usage.set(cpu)
            print(f"CPU 使用率: {cpu}%")

            # 記憶體使用率
            memory = psutil.virtual_memory()
            mem_usage.set(memory.percent)
            print(f"記憶體使用率: {memory.percent}%")

            # 每個磁碟的使用率
            for part in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    disk_usage.labels(mountpoint=part.mountpoint).set(usage.percent)
                    print(f"磁碟 {part.mountpoint} 使用率: {usage.percent}%")
                except PermissionError:
                    print(f"無法訪問磁碟 {part.mountpoint}: 權限錯誤")
                except Exception as e:
                    print(f"磁碟 {part.mountpoint} 錯誤: {e}")

            time.sleep(5)  # 每 5 秒更新一次
    except Exception as e:
        print(f"收集指標時發生錯誤: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    try:
        print("啟動 exporter...")
        start_http_server(8000, addr="0.0.0.0")
        print("Exporter 已啟動，訪問 http://localhost:8000/metrics 查看指標")
        collect_metrics()  # 注意：這行會一直執行，除非發生錯誤
    except Exception as e:
        print(f"啟動 exporter 時發生錯誤: {e}")
        traceback.print_exc()
        sys.exit(1)  # 非零退出碼表示錯誤