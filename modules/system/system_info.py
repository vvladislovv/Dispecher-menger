import platform
import psutil
import socket
import os
import time
from datetime import datetime, timedelta


class SystemInfo:
    @staticmethod
    def get_os_info():
        """Получение информации об операционной системе"""
        os_name = platform.system()
        os_version = platform.version()
        os_release = platform.release()
        os_arch = platform.machine()

        if os_name == "Windows":
            full_name = f"{os_name} {os_release} {os_version} {os_arch}"
        elif os_name == "Linux":
            try:
                with open("/etc/os-release") as f:
                    distro_info = dict(
                        line.strip().split("=", 1) for line in f if "=" in line
                    )
                full_name = f"{distro_info.get('NAME', 'Linux')} {distro_info.get('VERSION', '')}"
            except:
                full_name = f"{os_name} {os_release} {os_arch}"
        else:
            full_name = f"{os_name} {os_release} {os_arch}"

        return full_name

    @staticmethod
    def get_cpu_info():
        """Получение информации о процессоре"""
        cpu_info = {
            "name": "Неизвестно",
            "cores": psutil.cpu_count(logical=False),
            "threads": psutil.cpu_count(logical=True),
            "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
            "usage": psutil.cpu_percent(interval=0.1),
        }

        # Попытка получить имя процессора
        if platform.system() == "Windows":
            try:
                import winreg

                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
                )
                cpu_info["name"] = winreg.QueryValueEx(key, "ProcessorNameString")[0]
                winreg.CloseKey(key)
            except:
                pass
        elif platform.system() == "Linux":
            try:
                with open("/proc/cpuinfo") as f:
                    for line in f:
                        if line.strip().startswith("model name"):
                            cpu_info["name"] = line.split(":")[1].strip()
                            break
            except:
                pass
        elif platform.system() == "Darwin":  # macOS
            try:
                import subprocess

                cpu_info["name"] = (
                    subprocess.check_output(
                        ["sysctl", "-n", "machdep.cpu.brand_string"]
                    )
                    .decode()
                    .strip()
                )
            except:
                pass

        return cpu_info

    @staticmethod
    def get_memory_info():
        """Получение информации о памяти"""
        memory = psutil.virtual_memory()
        return {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percent": memory.percent,
        }

    @staticmethod
    def get_disk_info():
        """Получение информации о дисках"""
        disks = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append(
                    {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent,
                    }
                )
            except (PermissionError, FileNotFoundError):
                # Некоторые точки монтирования могут быть недоступны
                pass
        return disks

    @staticmethod
    def get_network_info():
        """Получение информации о сети"""
        try:
            hostname = socket.gethostname()
            # Используем более безопасный способ получения IP-адреса
            ip_address = "127.0.0.1"  # Локальный адрес по умолчанию

            # Попытка получить реальный IP-адрес
            try:
                # Создаем временное соединение для определения IP
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                # Не отправляем реальные данные
                s.connect(("8.8.8.8", 80))
                ip_address = s.getsockname()[0]
                s.close()
            except:
                # Если не удалось, используем локальный адрес
                pass

            # Получаем статистику сетевых интерфейсов
            net_io = psutil.net_io_counters()

            return {
                "hostname": hostname,
                "ip": ip_address,
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
            }
        except Exception as e:
            print(f"Ошибка при получении сетевой информации: {e}")
            return {
                "hostname": "Неизвестно",
                "ip": "Неизвестно",
                "bytes_sent": 0,
                "bytes_recv": 0,
                "packets_sent": 0,
                "packets_recv": 0,
            }

    @staticmethod
    def get_uptime():
        """Получение времени работы системы"""
        if platform.system() == "Windows":
            return time.time() - psutil.boot_time()
        else:
            try:
                with open("/proc/uptime", "r") as f:
                    uptime_seconds = float(f.readline().split()[0])
                    return uptime_seconds
            except:
                return time.time() - psutil.boot_time()

    @staticmethod
    def get_gpu_info():
        """Получение информации о видеокарте"""
        try:
            if platform.system() == "Windows":
                try:
                    import wmi

                    w = wmi.WMI()
                    gpu_info = w.Win32_VideoController()[0]
                    return {
                        "name": gpu_info.Name,
                        "driver_version": gpu_info.DriverVersion,
                    }
                except:
                    pass
            elif platform.system() == "Linux":
                try:
                    import subprocess

                    output = subprocess.check_output(
                        "lspci | grep -i vga", shell=True
                    ).decode()
                    return {"name": output.split(":")[-1].strip()}
                except:
                    pass
            elif platform.system() == "Darwin":  # macOS
                try:
                    import subprocess

                    output = subprocess.check_output(
                        "system_profiler SPDisplaysDataType | grep Chipset", shell=True
                    ).decode()
                    return {"name": output.split(":")[-1].strip()}
                except:
                    pass
        except Exception as e:
            print(f"Ошибка при получении информации о GPU: {e}")

        return {"name": "Неизвестно"}

    @staticmethod
    def get_motherboard_info():
        """Получение информации о материнской плате"""
        try:
            if platform.system() == "Windows":
                try:
                    import wmi

                    computer = wmi.WMI()
                    board = computer.Win32_BaseBoard()[0]
                    return {
                        "manufacturer": board.Manufacturer,
                        "product": board.Product,
                    }
                except:
                    pass
            elif platform.system() == "Linux":
                try:
                    manufacturer = "Неизвестно"
                    product = "Неизвестно"

                    try:
                        with open("/sys/class/dmi/id/board_vendor", "r") as f:
                            manufacturer = f.read().strip()
                    except:
                        pass

                    try:
                        with open("/sys/class/dmi/id/board_name", "r") as f:
                            product = f.read().strip()
                    except:
                        pass

                    return {"manufacturer": manufacturer, "product": product}
                except:
                    pass
            elif platform.system() == "Darwin":  # macOS
                try:
                    import subprocess

                    manufacturer = "Apple"
                    output = subprocess.check_output(
                        "system_profiler SPHardwareDataType | grep 'Model Name'",
                        shell=True,
                    ).decode()
                    product = output.split(":")[-1].strip()
                    return {"manufacturer": manufacturer, "product": product}
                except:
                    pass
        except Exception as e:
            print(f"Ошибка при получении информации о материнской плате: {e}")

        return {"manufacturer": "Неизвестно", "product": "Неизвестно"}

    @staticmethod
    def get_all_info():
        """Получение всей системной информации"""
        try:
            return {
                "os": SystemInfo.get_os_info(),
                "cpu": SystemInfo.get_cpu_info(),
                "memory": SystemInfo.get_memory_info(),
                "disks": SystemInfo.get_disk_info(),
                "network": SystemInfo.get_network_info(),
                "uptime": SystemInfo.get_uptime(),
                "gpu": SystemInfo.get_gpu_info(),
                "motherboard": SystemInfo.get_motherboard_info(),
            }
        except Exception as e:
            print(f"Ошибка при получении системной информации: {e}")
            return {
                "os": "Ошибка получения данных",
                "cpu": {
                    "name": "Ошибка",
                    "cores": 0,
                    "threads": 0,
                    "frequency": 0,
                    "usage": 0,
                },
                "memory": {"total": 0, "available": 0, "used": 0, "percent": 0},
                "disks": [],
                "network": {"hostname": "Ошибка", "ip": "Ошибка"},
                "uptime": 0,
                "gpu": {"name": "Ошибка"},
                "motherboard": {"manufacturer": "Ошибка", "product": "Ошибка"},
            }
