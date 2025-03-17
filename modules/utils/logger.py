import datetime
import os
import inspect
import traceback


class Logger:
    _instance = None
    _log_file = None
    _chat_callback = None
    _db_service = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Logger()
        return cls._instance

    def __init__(self):
        if Logger._instance is not None:
            raise Exception("Logger - это Singleton класс!")

        # Создаем директорию для логов, если её нет
        log_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs"
        )
        os.makedirs(log_dir, exist_ok=True)

        # Создаем файл лога с текущей датой
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        log_path = os.path.join(log_dir, f"log_{current_date}.log")
        self._log_file = open(log_path, "a", encoding="utf-8")

        # Инициализируем сервис базы данных позже, чтобы избежать циклических импортов
        self._db_service = None
        self._db_initialized = False

    def _init_db_service(self):
        """Инициализирует сервис базы данных при первом использовании"""
        if not self._db_initialized:
            try:
                # Импортируем здесь, чтобы избежать циклических импортов
                from modules.database.db_service import get_db_service

                self._db_service = get_db_service()
                self._db_initialized = True
            except ImportError:
                # Если модуль еще не доступен, пропускаем инициализацию
                pass

    def set_chat_callback(self, callback):
        """Устанавливает функцию обратного вызова для отображения логов в чате"""
        self._chat_callback = callback

    def log(self, message, level="INFO"):
        """Записывает сообщение в лог и отправляет в чат, если установлен callback"""
        # Получаем информацию о вызывающем файле и функции
        caller_frame = inspect.currentframe().f_back
        caller_info = inspect.getframeinfo(caller_frame)
        file_name = os.path.basename(caller_info.filename)
        line_number = caller_info.lineno
        function_name = caller_info.function
        source = f"{file_name}:{function_name}:{line_number}"

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] [{source}] {message}"

        # Запись в файл
        self._log_file.write(log_message + "\n")
        self._log_file.flush()

        # Отправка в чат, если установлен callback
        if self._chat_callback:
            self._chat_callback(log_message)

        # Сохранение в базу данных (отложенная инициализация)
        try:
            self._init_db_service()
            if self._db_service and self._db_initialized:
                self._db_service.add_log(level, source, message)
        except Exception as e:
            # Не используем self.error() здесь, чтобы избежать рекурсии
            print(f"Ошибка при сохранении лога в базу данных: {str(e)}")

        return log_message

    def info(self, message):
        return self.log(message, "INFO")

    def warning(self, message):
        return self.log(message, "WARNING")

    def error(self, message, include_traceback=True):
        if include_traceback:
            tb = traceback.format_exc()
            if tb != "NoneType: None\n":
                message = f"{message}\n{tb}"
        return self.log(message, "ERROR")

    def debug(self, message):
        return self.log(message, "DEBUG")

    def exception(self, e, message="Произошло исключение:"):
        """Логирует исключение с трассировкой"""
        error_message = f"{message} {str(e)}"
        tb = traceback.format_exc()
        return self.log(f"{error_message}\n{tb}", "ERROR")

    def __del__(self):
        if self._log_file:
            self._log_file.close()


# Создаем глобальный экземпляр логгера
_logger_instance = None


def get_logger():
    """
    Создает и возвращает настроенный логгер для приложения.

    Возвращает:
        Logger: Настроенный объект логгера

    Действия:
        1. Создает логгер с именем 'system_monitor'
        2. Настраивает форматирование сообщений
        3. Добавляет обработчики для вывода в консоль и файл
        4. Настраивает уровень логирования
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = Logger.get_instance()
    return _logger_instance


# Убедимся, что функция доступна при импорте
__all__ = ["Logger", "get_logger"]
