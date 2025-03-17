import psutil
import time
import threading
import queue


class ProcessMonitor:
    def __init__(self):
        self.processes = []
        self.running = False
        self.update_interval = 2  # секунды
        self.lock = threading.Lock()
        self.callbacks = []
        self.callback_queue = queue.Queue()

    def start_monitoring(self):
        """Запуск мониторинга процессов"""
        if self.running:
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_processes)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Остановка мониторинга процессов"""
        self.running = False
        if hasattr(self, "monitor_thread"):
            self.monitor_thread.join(timeout=1)

    def _monitor_processes(self):
        """Фоновый мониторинг процессов"""
        while self.running:
            try:
                new_processes = self._get_processes()
                with self.lock:
                    self.processes = new_processes

                # Вместо прямого вызова callback, помещаем данные в очередь
                # для последующей обработки в основном потоке
                for callback in self.callbacks:
                    self.callback_queue.put((callback, self.processes.copy()))

                time.sleep(self.update_interval)
            except Exception as e:
                print(f"Ошибка при мониторинге процессов: {e}")
                time.sleep(1)

    def process_callbacks(self):
        """Обработка обратных вызовов в основном потоке"""
        try:
            while not self.callback_queue.empty():
                callback, processes = self.callback_queue.get_nowait()
                callback(processes)
                self.callback_queue.task_done()
        except Exception as e:
            print(f"Ошибка при обработке callback: {e}")

    def _get_processes(self):
        """Получение списка процессов"""
        processes = []
        try:
            # Получаем все процессы
            all_processes = []
            for proc in psutil.process_iter(["pid", "name", "status"]):
                try:
                    # Получаем информацию о процессе
                    process_info = proc.info
                    pid = process_info["pid"]
                    name = process_info["name"]
                    status = process_info["status"]

                    # Получаем использование памяти и CPU
                    with proc.oneshot():
                        memory_info = proc.memory_info()
                        memory_mb = memory_info.rss / (1024 * 1024)
                        cpu_percent = proc.cpu_percent(interval=None)

                    all_processes.append(
                        [name, str(pid), memory_mb, cpu_percent, status]
                    )
                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
                ):
                    pass

            # Сортируем по использованию памяти (от большего к меньшему)
            all_processes.sort(key=lambda x: x[2], reverse=True)

            # Берем только первые 50 процессов
            top_processes = all_processes[:50]

            # Форматируем значения для отображения
            for proc in top_processes:
                proc[2] = f"{proc[2]:.1f}"  # Форматируем память
                proc[3] = f"{proc[3]:.1f}"  # Форматируем CPU
                processes.append(proc)

        except Exception as e:
            print(f"Ошибка при получении списка процессов: {e}")

        return processes

    def get_processes(self):
        """Получение текущего списка процессов"""
        with self.lock:
            return self.processes.copy()

    def kill_process(self, pid):
        """Завершение процесса по PID"""
        try:
            pid = int(pid)
            process = psutil.Process(pid)
            process.terminate()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, ValueError):
            return False

    def register_callback(self, callback):
        """Регистрация функции обратного вызова для обновления UI"""
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def unregister_callback(self, callback):
        """Отмена регистрации функции обратного вызова"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
