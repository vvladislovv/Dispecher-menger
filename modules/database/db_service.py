from modules.database.db_models import init_db, Log, TerminatedProcess
import datetime
import os
import sys

# Добавляем путь к корневой директории проекта в sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Инициализация базы данных
engine, Session = init_db()

# Глобальный экземпляр сервиса
_db_service_instance = None


class DatabaseService:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DatabaseService()
        return cls._instance

    def __init__(self):
        if DatabaseService._instance is not None:
            raise Exception("DatabaseService - это Singleton класс!")

        print("Инициализация сервиса базы данных")
        self.engine = engine
        self.Session = Session

    def add_log(self, level, source, message):
        """Добавляет запись лога в базу данных"""
        try:
            session = self.Session()
            log = Log(
                timestamp=datetime.datetime.now(),
                level=level,
                source=source,
                message=message,
            )
            session.add(log)
            session.commit()
            print(f"Лог добавлен в базу данных: {level} - {source}")
            return log.id
        except Exception as e:
            print(f"Ошибка при добавлении лога в базу данных: {str(e)}")
            session.rollback()
            return None
        finally:
            session.close()

    def add_terminated_process(self, process_data, terminated_by="user"):
        """
        Добавляет информацию о завершенном процессе в базу данных.

        Аргументы:
            process_data (list): Список с информацией о процессе в формате
                [name, pid, memory, cpu, status]
            terminated_by (str, optional): Кто завершил процесс (по умолчанию "user")

        Возвращает:
            int или None: ID записи в базе данных или None в случае ошибки

        Действия:
            1. Распаковывает данные процесса
            2. Преобразует строковые значения в числовые
            3. Создает запись в таблице terminated_processes
            4. Сохраняет запись в базе данных
        """
        session = None
        try:
            session = self.Session()

            # Распаковываем данные процесса
            name, pid, memory, cpu, status = process_data

            print(f"Добавление процесса в БД: {name}, {pid}, {memory}, {cpu}, {status}")

            # Преобразуем строковые значения в числовые
            try:
                # Очищаем строку от нечисловых символов, кроме точки
                memory_str = "".join(c for c in str(memory) if c.isdigit() or c == ".")
                memory_float = float(memory_str) if memory_str else 0.0
            except Exception as e:
                print(f"Ошибка преобразования памяти '{memory}': {str(e)}")
                memory_float = 0.0

            try:
                # Очищаем строку от нечисловых символов, кроме точки
                cpu_str = "".join(c for c in str(cpu) if c.isdigit() or c == ".")
                cpu_float = float(cpu_str) if cpu_str else 0.0
            except Exception as e:
                print(f"Ошибка преобразования CPU '{cpu}': {str(e)}")
                cpu_float = 0.0

            # Создаем новую запись
            terminated_process = TerminatedProcess(
                timestamp=datetime.datetime.now(),
                process_name=str(name),
                pid=str(pid),
                memory_usage=memory_float,
                cpu_usage=cpu_float,
                status=str(status),
                terminated_by=str(terminated_by),
            )

            session.add(terminated_process)
            session.commit()
            print(
                f"Информация о завершенном процессе добавлена в базу данных: {name} (PID: {pid})"
            )
            return terminated_process.id
        except Exception as e:
            import traceback

            print(f"Ошибка при добавлении информации о завершенном процессе: {str(e)}")
            print(traceback.format_exc())
            if session:
                session.rollback()
            return None
        finally:
            if session:
                session.close()

    def get_logs(self, limit=100, level=None, start_date=None, end_date=None):
        """Получает логи из базы данных с возможностью фильтрации"""
        try:
            session = self.Session()
            query = session.query(Log)

            # Применяем фильтры, если они указаны
            if level:
                query = query.filter(Log.level == level)

            if start_date:
                query = query.filter(Log.timestamp >= start_date)

            if end_date:
                query = query.filter(Log.timestamp <= end_date)

            # Сортируем по времени (сначала новые)
            query = query.order_by(Log.timestamp.desc())

            # Ограничиваем количество результатов
            if limit:
                query = query.limit(limit)

            logs = query.all()
            print(f"Получено {len(logs)} логов из базы данных")
            return logs
        except Exception as e:
            print(f"Ошибка при получении логов из базы данных: {str(e)}")
            return []
        finally:
            session.close()

    def get_terminated_processes(self, limit=100, start_date=None, end_date=None):
        """Получает информацию о завершенных процессах из базы данных"""
        try:
            session = self.Session()
            query = session.query(TerminatedProcess)

            # Применяем фильтры, если они указаны
            if start_date:
                query = query.filter(TerminatedProcess.timestamp >= start_date)

            if end_date:
                query = query.filter(TerminatedProcess.timestamp <= end_date)

            # Сортируем по времени (сначала новые)
            query = query.order_by(TerminatedProcess.timestamp.desc())

            # Ограничиваем количество результатов
            if limit:
                query = query.limit(limit)

            processes = query.all()
            print(
                f"Получено {len(processes)} записей о завершенных процессах из базы данных"
            )
            return processes
        except Exception as e:
            print(f"Ошибка при получении информации о завершенных процессах: {str(e)}")
            return []
        finally:
            session.close()


# Функция для получения экземпляра сервиса базы данных
def get_db_service():
    global _db_service_instance
    if _db_service_instance is None:
        _db_service_instance = DatabaseService.get_instance()
    return _db_service_instance
