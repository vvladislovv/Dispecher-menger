import psutil
import platform
import os
from modules.utils.logger import get_logger

# Инициализация логгера
logger = get_logger()


class SystemInfo:
    @staticmethod
    def get_system_info():
        """Получение общей информации о системе"""
        logger.info("Получение информации о системе")
        try:
            info = {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "cpu_count": psutil.cpu_count(logical=True),
                "physical_cpu_count": psutil.cpu_count(logical=False),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
            }
            logger.debug(f"Информация о системе: {info}")
            return info
        except Exception as e:
            logger.exception(e, "Ошибка при получении информации о системе:")
            return {}


class ProcessHandler:
    @staticmethod
    def get_all_processes():
        """Получение списка всех процессов в системе"""
        logger.info("Получение списка всех процессов")
        try:
            processes = []
            for proc in psutil.process_iter(
                ["pid", "name", "memory_info", "cpu_percent", "status"]
            ):
                try:
                    # Получение информации о процессе
                    process_info = proc.info
                    pid = str(process_info["pid"])
                    name = process_info["name"]
                    memory = f"{process_info['memory_info'].rss / (1024 * 1024):.2f}"
                    cpu = f"{process_info['cpu_percent']:.1f}"
                    status = process_info["status"]

                    processes.append([name, pid, memory, cpu, status])
                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
                ) as e:
                    logger.warning(
                        f"Не удалось получить информацию о процессе: {str(e)}"
                    )
                    continue

            logger.info(f"Получено {len(processes)} процессов")
            return processes
        except Exception as e:
            logger.exception(e, "Ошибка при получении списка процессов:")
            return []

    @staticmethod
    def terminate_process(pid):
        """Завершение процесса по PID"""
        logger.warning(f"Попытка завершения процесса с PID: {pid}")
        try:
            process = psutil.Process(int(pid))
            process.terminate()
            logger.info(f"Процесс с PID {pid} успешно завершен")
            return True
        except psutil.NoSuchProcess:
            logger.error(f"Процесс с PID {pid} не найден")
            return False
        except psutil.AccessDenied:
            logger.error(
                f"Отказано в доступе при попытке завершить процесс с PID {pid}"
            )
            try:
                # Попытка завершить процесс с повышенными привилегиями
                if os.name == "nt":  # Windows
                    import subprocess

                    subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=True)
                else:  # Linux/Mac
                    import subprocess

                    subprocess.run(["sudo", "kill", "-9", str(pid)], check=True)
                logger.info(
                    f"Процесс с PID {pid} успешно завершен с повышенными привилегиями"
                )
                return True
            except Exception as e:
                logger.exception(
                    e,
                    f"Не удалось завершить процесс с PID {pid} с повышенными привилегиями:",
                )
                return False
        except Exception as e:
            logger.exception(e, f"Ошибка при завершении процесса с PID {pid}:")
            return False

    @staticmethod
    def get_performance_data():
        """Получение данных о производительности системы"""
        logger.debug("Получение данных о производительности системы")
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used / (1024 * 1024 * 1024)  # В ГБ
            memory_total = memory.total / (1024 * 1024 * 1024)  # В ГБ

            disk_usage = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.device] = {
                        "total": usage.total / (1024 * 1024 * 1024),  # В ГБ
                        "used": usage.used / (1024 * 1024 * 1024),  # В ГБ
                        "percent": usage.percent,
                    }
                except Exception as e:
                    logger.warning(
                        f"Не удалось получить информацию о диске {partition.device}: {str(e)}"
                    )

            network_io = psutil.net_io_counters()

            data = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_used": memory_used,
                "memory_total": memory_total,
                "disk_usage": disk_usage,
                "network_sent": network_io.bytes_sent,
                "network_recv": network_io.bytes_recv,
            }

            logger.debug("Данные о производительности системы получены успешно")
            return data
        except Exception as e:
            logger.exception(
                e, "Ошибка при получении данных о производительности системы:"
            )
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
                "memory_used": 0,
                "memory_total": 0,
                "disk_usage": {},
                "network_sent": 0,
                "network_recv": 0,
            }
