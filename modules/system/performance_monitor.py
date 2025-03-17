import psutil
import time
import threading
import queue
from collections import deque


class PerformanceMonitor:
    def __init__(self, history_length=60):
        self.cpu_history = deque(maxlen=history_length)
        self.memory_history = deque(maxlen=history_length)
        self.disk_io_history = deque(maxlen=history_length)
        self.network_history = deque(maxlen=history_length)

        self.running = False
        self.update_interval = 1  # секунды
        self.callbacks = []
        self.callback_queue = queue.Queue()

        # Инициализация начальных значений для расчета скорости
        self.last_disk_read = 0
        self.last_disk_write = 0
        self.last_net_sent = 0
        self.last_net_recv = 0
        self.last_time = time.time()

    def start_monitoring(self):
        """Запуск мониторинга производительности"""
        if self.running:
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_performance)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Остановка мониторинга производительности"""
        self.running = False
        if hasattr(self, "monitor_thread"):
            self.monitor_thread.join(timeout=1)

    def _monitor_performance(self):
        """Фоновый мониторинг производительности"""
        while self.running:
            try:
                current_time = time.time()
                time_diff = current_time - self.last_time

                # CPU
                cpu_percent = psutil.cpu_percent(interval=None)
                self.cpu_history.append(cpu_percent)

                # Память
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                self.memory_history.append(memory_percent)

                # Диск I/O
                disk_io = psutil.disk_io_counters()
                if disk_io:
                    read_speed = (
                        (disk_io.read_bytes - self.last_disk_read)
                        / time_diff
                        / (1024 * 1024)
                    )  # МБ/с
                    write_speed = (
                        (disk_io.write_bytes - self.last_disk_write)
                        / time_diff
                        / (1024 * 1024)
                    )  # МБ/с
                    self.disk_io_history.append((read_speed, write_speed))
                    self.last_disk_read = disk_io.read_bytes
                    self.last_disk_write = disk_io.write_bytes

                # Сеть
                net_io = psutil.net_io_counters()
                sent_speed = (
                    (net_io.bytes_sent - self.last_net_sent) / time_diff / (1024 * 1024)
                )  # МБ/с
                recv_speed = (
                    (net_io.bytes_recv - self.last_net_recv) / time_diff / (1024 * 1024)
                )  # МБ/с
                self.network_history.append((sent_speed, recv_speed))
                self.last_net_sent = net_io.bytes_sent
                self.last_net_recv = net_io.bytes_recv

                self.last_time = current_time

                # Подготавливаем данные для обратных вызовов
                performance_data = {
                    "cpu": {"current": cpu_percent, "history": list(self.cpu_history)},
                    "memory": {
                        "current": memory_percent,
                        "total": memory.total,
                        "used": memory.used,
                        "history": list(self.memory_history),
                    },
                    "disk_io": {
                        "current": (read_speed, write_speed) if disk_io else (0, 0),
                        "history": list(self.disk_io_history),
                    },
                    "network": {
                        "current": (sent_speed, recv_speed),
                        "history": list(self.network_history),
                    },
                }

                # Помещаем данные в очередь для обработки в основном потоке
                for callback in self.callbacks:
                    self.callback_queue.put((callback, performance_data))

                time.sleep(self.update_interval)
            except Exception as e:
                print(f"Ошибка при мониторинге производительности: {e}")
                time.sleep(1)

    def process_callbacks(self):
        """Обработка обратных вызовов в основном потоке"""
        try:
            while not self.callback_queue.empty():
                callback, data = self.callback_queue.get_nowait()
                callback(data)
                self.callback_queue.task_done()
        except Exception as e:
            print(f"Ошибка при обработке callback: {e}")

    def get_current_data(self):
        """Получение текущих данных о производительности"""
        cpu_percent = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()

        return {
            "cpu": {"current": cpu_percent, "history": list(self.cpu_history)},
            "memory": {
                "current": memory.percent,
                "total": memory.total,
                "used": memory.used,
                "history": list(self.memory_history),
            },
            "disk_io": {"history": list(self.disk_io_history)},
            "network": {"history": list(self.network_history)},
        }

    def register_callback(self, callback):
        """Регистрация функции обратного вызова для обновления UI"""
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def unregister_callback(self, callback):
        """Отмена регистрации функции обратного вызова"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
