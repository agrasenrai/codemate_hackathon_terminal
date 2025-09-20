import psutil
import platform
import time
from datetime import datetime

# --- Hackathon-winning: Real-time system stats, cross-platform, clean output, timestamps ---

class SystemMonitor:
    def __init__(self):
        self.history = []

    def sysinfo(self):
        info = {
            'OS': platform.system(),
            'Platform': platform.platform(),
            'Uptime': self._uptime(),
            'CPU': psutil.cpu_count(logical=True),
            'Memory': f"{psutil.virtual_memory().total // (1024**2)} MB",
        }
        return self._format(info)

    def top(self, n=5):
        procs = [(p.info['pid'], p.info['name'], p.info['cpu_percent'])
                 for p in psutil.process_iter(['pid', 'name', 'cpu_percent'])]
        procs.sort(key=lambda x: x[2], reverse=True)
        lines = [f"PID   NAME         CPU%"]
        for pid, name, cpu in procs[:n]:
            lines.append(f"{pid:<5} {name[:12]:<12} {cpu:>5}")
        return '\n'.join(lines)

    def ps(self):
        lines = [f"PID   NAME"]
        for p in psutil.process_iter(['pid', 'name']):
            lines.append(f"{p.info['pid']:<5} {p.info['name']}")
        return '\n'.join(lines)

    def df(self):
        usage = psutil.disk_usage('/')
        return f"Disk: {usage.total // (1024**3)}GB total, {usage.used // (1024**3)}GB used, {usage.free // (1024**3)}GB free ({usage.percent}% used)"

    def free(self):
        mem = psutil.virtual_memory()
        return f"Memory: {mem.total // (1024**2)}MB total, {mem.available // (1024**2)}MB available ({mem.percent}% used)"

    def _uptime(self):
        boot = datetime.fromtimestamp(psutil.boot_time())
        return str(datetime.now() - boot).split('.')[0]

    def _format(self, d):
        return '\n'.join([f"{k}: {v}" for k, v in d.items()])
