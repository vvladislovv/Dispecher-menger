import time
import threading
from collections import deque
from modules.utils.logger import get_logger
from modules.system.process_handler import ProcessHandler
from modules.config.settings import MONITORING_SETTINGS

# Инициализация логгера
logger = get_logger()


class PerformanceMonitor:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = PerformanceMonitor()
        return cls._instance

    def __init__(self):
        if PerformanceMonitor._instance is not None:
            raise Exception("PerformanceMonitor - это Singleton класс!")

        logger.info("Инициализация монитора производительности")

        # Инициализация хранилища данных
        self.cpu_history = deque(
            maxlen=MONITORING_SETTINGS["performance_history_length"]
        )
        self.memory_history = deque(
            maxlen=MONITORING_SETTINGS["performance_history_length"]
        )
        self.disk_history = {}
        self.network_history = {
            "sent": deque(maxlen=MONITORING_SETTINGS["performance_history_length"]),
            "recv": deque(maxlen=MONITORING_SETTINGS["performance_history_length"]),
        }

        # Флаг для управления мониторингом
        self.is_monitoring = False
        self.monitor_thread = None

        # Обратные вызовы для обновления UI
        self.update_callbacks = []

        logger.info("Монитор производительности инициализирован")

    def add_update_callback(self, callback):
        """Добавляет функцию обратного вызова для обновления UI"""
        logger.debug(
            f"Добавлен callback для обновления UI: {callback.__name__ if hasattr(callback, '__name__') else 'anonymous'}"
        )
        self.update_callbacks.append(callback)

    def start_monitoring(self):
        """Запускает мониторинг производительности в отдельном потоке"""
        if self.is_monitoring:
            logger.warning("Мониторинг уже запущен")
            return

        logger.info("Запуск мониторинга производительности")
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Останавливает мониторинг производительности"""
        if not self.is_monitoring:
            logger.warning("Мониторинг уже остановлен")
            return

        logger.info("Остановка мониторинга производительности")
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)

    def _monitoring_loop(self):
        """Основной цикл мониторинга"""
        logger.info("Запущен цикл мониторинга производительности")
        last_network_sent = 0
        last_network_recv = 0

        while self.is_monitoring:
            try:
                # Получаем данные о производительности
                data = ProcessHandler.get_performance_data()

                # Добавляем данные в историю
                self.cpu_history.append(data["cpu_percent"])
                self.memory_history.append(data["memory_percent"])

                # Обрабатываем данные о дисках
                for device, usage in data["disk_usage"].items():
                    if device not in self.disk_history:
                        self.disk_history[device] = deque(
                            maxlen=MONITORING_SETTINGS["performance_history_length"]
                        )
                    self.disk_history[device].append(usage["percent"])

                # Обрабатываем данные о сети (вычисляем скорость)
                current_sent = data["network_sent"]
                current_recv = data["network_recv"]

                if last_network_sent > 0:
                    sent_speed = (
                        current_sent - last_network_sent
                    ) / MONITORING_SETTINGS["performance_update_interval"]
                    self.network_history["sent"].append(sent_speed)

                if last_network_recv > 0:
                    recv_speed = (
                        current_recv - last_network_recv
                    ) / MONITORING_SETTINGS["performance_update_interval"]
                    self.network_history["recv"].append(recv_speed)

                last_network_sent = current_sent
                last_network_recv = current_recv

                # Вызываем все обратные вызовы для обновления UI
                for callback in self.update_callbacks:
                    try:
                        callback(data)
                    except Exception as e:
                        logger.exception(
                            e,
                            f"Ошибка в callback {callback.__name__ if hasattr(callback, '__name__') else 'anonymous'}:",
                        )

                # Ждем до следующего обновления
                time.sleep(MONITORING_SETTINGS["performance_update_interval"])
            except Exception as e:
                logger.exception(e, "Ошибка в цикле мониторинга производительности:")
                time.sleep(1)  # Пауза перед повторной попыткой

        logger.info("Цикл мониторинга производительности завершен")

    def get_current_data(self):
        """Возвращает текущие данные о производительности"""
        logger.debug("Запрос текущих данных о производительности")
        try:
            return {
                "cpu": list(self.cpu_history),
                "memory": list(self.memory_history),
                "disk": {
                    device: list(history)
                    for device, history in self.disk_history.items()
                },
                "network": {
                    "sent": list(self.network_history["sent"]),
                    "recv": list(self.network_history["recv"]),
                },
            }
        except Exception as e:
            logger.exception(
                e, "Ошибка при получении текущих данных о производительности:"
            )
            return {
                "cpu": [],
                "memory": [],
                "disk": {},
                "network": {"sent": [], "recv": []},
            }


# Функция для получения экземпляра монитора производительности
def get_performance_monitor():
    return PerformanceMonitor.get_instance()
