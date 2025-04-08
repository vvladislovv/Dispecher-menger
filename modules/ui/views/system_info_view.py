import flet as ft
from modules.system.system_info import SystemInfo
import threading
import platform
import psutil
import time
import subprocess


class SystemInfoView(ft.Container):
    def __init__(self):
        super().__init__()
        self.system_info = None
        self.system_data = None
        self.loading = True
        self.uptime_timer = None
        self.uptime_timer_running = True
        self.uptime_row = None  # Добавляем ссылку на строку с временем работы

        # Создаем индикатор загрузки
        self.info_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Загрузка информации о системе...",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.ProgressRing(),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=15,
            expand=True,
        )

        # Настраиваем контейнер
        self.content = ft.Column(
            [
                ft.Text(
                    "О системе",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                self.info_container,
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
        )
        self.padding = 20
        self.expand = True
        self.alignment = ft.alignment.center

    def did_mount(self):
        # Загружаем системную информацию при монтировании компонента
        self.load_system_info()

        # Запускаем таймер для обновления времени работы
        self.start_uptime_timer()

    def will_unmount(self):
        # Останавливаем таймер при размонтировании компонента
        self.stop_uptime_timer()

    def load_system_info(self):
        """Загрузка системной информации"""
        try:
            self.system_info = SystemInfo.get_all_info()

            # Исправляем отображение операционной системы
            if self.system_info["os"] == "Darwin":
                # Получаем более подробную информацию о версии macOS
                try:
                    # Получаем версию macOS из системной команды
                    mac_version = (
                        subprocess.check_output("sw_vers -productVersion", shell=True)
                        .decode()
                        .strip()
                    )

                    # Получаем название macOS из системной команды
                    mac_name = (
                        subprocess.check_output("sw_vers -productName", shell=True)
                        .decode()
                        .strip()
                    )

                    # Определяем полное название версии macOS
                    full_name = mac_name
                    version_parts = mac_version.split(".")

                    # Добавляем кодовое название, если известно
                    if version_parts[0] == "14":
                        full_name = "macOS Sonoma"
                    elif version_parts[0] == "13":
                        full_name = "macOS Ventura"
                    elif version_parts[0] == "12":
                        full_name = "macOS Monterey"
                    elif version_parts[0] == "11":
                        full_name = "macOS Big Sur"
                    elif version_parts[0] == "10":
                        if version_parts[1] == "15":
                            full_name = "macOS Catalina"
                        elif version_parts[1] == "14":
                            full_name = "macOS Mojave"
                        elif version_parts[1] == "13":
                            full_name = "macOS High Sierra"
                        elif version_parts[1] == "12":
                            full_name = "macOS Sierra"
                        elif version_parts[1] == "11":
                            full_name = "OS X El Capitan"
                        elif version_parts[1] == "10":
                            full_name = "OS X Yosemite"
                        elif version_parts[1] == "9":
                            full_name = "OS X Mavericks"
                        elif version_parts[1] == "8":
                            full_name = "OS X Mountain Lion"
                        elif version_parts[1] == "7":
                            full_name = "OS X Lion"

                    # Устанавливаем полное название с версией
                    self.system_info["os"] = f"{full_name} {mac_version}"

                    # Выводим информацию в консоль для отладки
                    print(f"Определена операционная система: {self.system_info['os']}")

                except Exception as e:
                    print(f"Ошибка при определении версии macOS: {e}")
                    # Если не удалось получить подробную информацию, используем стандартный метод
                    self.system_info["os"] = f"macOS {platform.mac_ver()[0]}"

            # Исправляем отображение материнской платы
            self.fix_motherboard_info()

            self.system_data = self.system_info
            self.loading = False
            self.update_ui()
        except Exception as e:
            print(f"Ошибка при загрузке системной информации: {e}")
            self.loading = False
            self.info_container.content = ft.Column(
                [
                    ft.Text(
                        "Ошибка при загрузке информации о системе",
                        size=16,
                        color=ft.colors.ERROR,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        f"Подробности: {str(e)}",
                        size=14,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.ElevatedButton(
                        "Повторить загрузку",
                        on_click=lambda _: self.reload_info(),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            )
            self.update()

    def fix_motherboard_info(self):
        """Исправление информации о материнской плате для macOS"""
        try:
            # Проверяем, есть ли информация о материнской плате
            if (
                not self.system_info.get("motherboard")
                or not self.system_info["motherboard"].get("manufacturer")
                or not self.system_info["motherboard"].get("product")
                or self.system_info["motherboard"]["manufacturer"] == "Unknown"
                or self.system_info["motherboard"]["product"] == "Unknown"
            ):
                # Пытаемся получить информацию о материнской плате другим способом
                if platform.system() == "Darwin":  # macOS
                    try:
                        # Получаем модель Mac
                        model = (
                            subprocess.check_output("sysctl -n hw.model", shell=True)
                            .decode()
                            .strip()
                        )

                        # Получаем более подробную информацию о модели
                        system_profiler = subprocess.check_output(
                            "system_profiler SPHardwareDataType", shell=True
                        ).decode()

                        # Извлекаем производителя (всегда Apple для Mac)
                        manufacturer = "Apple"

                        # Извлекаем модель из вывода system_profiler
                        product = model
                        for line in system_profiler.split("\n"):
                            if "Model Name" in line or "Model Identifier" in line:
                                parts = line.split(":")
                                if len(parts) > 1 and parts[1].strip():
                                    product = parts[1].strip()
                                    break

                        if not self.system_info.get("motherboard"):
                            self.system_info["motherboard"] = {}

                        self.system_info["motherboard"]["manufacturer"] = manufacturer
                        self.system_info["motherboard"]["product"] = product
                    except:
                        # Если не удалось получить информацию, устанавливаем значения по умолчанию
                        if not self.system_info.get("motherboard"):
                            self.system_info["motherboard"] = {}

                        self.system_info["motherboard"]["manufacturer"] = "Apple"
                        self.system_info["motherboard"]["product"] = "Mac"

                elif platform.system() == "Windows":
                    # Код для Windows остается без изменений
                    result = subprocess.check_output(
                        "wmic baseboard get product,manufacturer", shell=True
                    ).decode()
                    lines = result.strip().split("\n")
                    if len(lines) > 1:
                        parts = lines[1].split()
                        if parts:
                            manufacturer = parts[0]
                            product = (
                                " ".join(parts[1:]) if len(parts) > 1 else "Unknown"
                            )

                            if not self.system_info.get("motherboard"):
                                self.system_info["motherboard"] = {}

                            self.system_info["motherboard"][
                                "manufacturer"
                            ] = manufacturer
                            self.system_info["motherboard"]["product"] = product

                elif platform.system() == "Linux":
                    # Код для Linux остается без изменений
                    try:
                        manufacturer = (
                            subprocess.check_output(
                                "cat /sys/devices/virtual/dmi/id/board_vendor 2>/dev/null || echo 'Unknown'",
                                shell=True,
                            )
                            .decode()
                            .strip()
                        )
                        product = (
                            subprocess.check_output(
                                "cat /sys/devices/virtual/dmi/id/board_name 2>/dev/null || echo 'Unknown'",
                                shell=True,
                            )
                            .decode()
                            .strip()
                        )

                        if not self.system_info.get("motherboard"):
                            self.system_info["motherboard"] = {}

                        self.system_info["motherboard"]["manufacturer"] = manufacturer
                        self.system_info["motherboard"]["product"] = product
                    except:
                        pass
        except Exception as e:
            print(f"Ошибка при получении информации о материнской плате: {e}")

    def reload_info(self):
        """Повторная загрузка информации о системе"""
        self.loading = True
        self.info_container.content = ft.Column(
            [
                ft.Text(
                    "Загрузка информации о системе...",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.ProgressRing(),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.update()
        self.load_system_info()

    def update_ui(self):
        """Обновление UI с системной информацией"""
        if not self.system_info:
            return

        # Создаем контейнер с общей информацией
        general_info = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Общая информация",
                        weight=ft.FontWeight.BOLD,
                        size=18,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Divider(),
                    self.create_info_row(
                        "Операционная система:", self.system_info["os"]
                    ),
                    self.create_info_row("Процессор:", self.system_info["cpu"]["name"]),
                    self.create_info_row(
                        "Ядра / Потоки:",
                        f"{self.system_info['cpu']['cores']} / {self.system_info['cpu']['threads']}",
                    ),
                    self.create_info_row(
                        "Частота процессора:",
                        f"{self.system_info['cpu']['frequency']:.2f} МГц",
                    ),
                    self.create_info_row(
                        "Материнская плата:",
                        f"{self.system_info['motherboard']['manufacturer']} {self.system_info['motherboard']['product']}",
                    ),
                    self.create_info_row(
                        "Видеокарта:", self.system_info["gpu"]["name"]
                    ),
                ],
                spacing=10,
            ),
            padding=15,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
        )

        # Создаем контейнер с информацией о памяти
        memory_info = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Память",
                        weight=ft.FontWeight.BOLD,
                        size=18,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Divider(),
                    self.create_info_row(
                        "Оперативная память:",
                        f"{self.system_info['memory']['used'] / (1024**3):.1f} ГБ / {self.system_info['memory']['total'] / (1024**3):.1f} ГБ ({self.system_info['memory']['percent']}%)",
                    ),
                    ft.ProgressBar(
                        value=self.system_info["memory"]["percent"] / 100,
                        bgcolor=ft.colors.BLACK12,
                        color=(
                            ft.colors.BLUE
                            if self.system_info["memory"]["percent"] < 90
                            else ft.colors.RED
                        ),
                        height=10,
                    ),
                    self.create_info_row(
                        "Доступно:",
                        f"{self.system_info['memory']['available'] / (1024**3):.1f} ГБ",
                    ),
                ],
                spacing=10,
            ),
            padding=15,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
        )

        # Создаем контейнер с информацией о сети
        network_info = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Сеть",
                        weight=ft.FontWeight.BOLD,
                        size=18,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Divider(),
                    self.create_info_row(
                        "Имя хоста:", self.system_info["network"]["hostname"]
                    ),
                    self.create_info_row(
                        "IP-адрес:", self.system_info["network"]["ip"]
                    ),
                    self.create_info_row(
                        "Отправлено:",
                        f"{self.system_info['network']['bytes_sent'] / (1024**2):.1f} МБ",
                    ),
                    self.create_info_row(
                        "Получено:",
                        f"{self.system_info['network']['bytes_recv'] / (1024**2):.1f} МБ",
                    ),
                ],
                spacing=10,
            ),
            padding=15,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
        )

        # Создаем контейнер с информацией о времени работы
        uptime_info = self.create_uptime_info()

        # Создаем контейнер с информацией о дисках
        disks_info = self.create_disks_info()

        # Обновляем контейнер с информацией
        self.info_container.content = ft.Column(
            [
                general_info,
                ft.Container(height=20),
                memory_info,
                ft.Container(height=20),
                network_info,
                ft.Container(height=20),
                uptime_info,
                ft.Container(height=20),
                disks_info,
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        self.update()

    def create_info_row(self, label, value):
        return ft.Row(
            [
                ft.Text(label, weight=ft.FontWeight.BOLD),
                ft.Text(str(value)),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def create_disks_info(self):
        """Создание контейнера с информацией о дисках с улучшенным отображением для macOS"""
        disks_rows = []

        if self.system_info and "disks" in self.system_info:
            # Фильтруем диски для macOS
            physical_disks = []
            for disk in self.system_info["disks"]:
                device = disk.get("device", "")
                mountpoint = disk.get("mountpoint", "")

                # На macOS показываем только основные диски
                if platform.system() == "Darwin":
                    # Включаем основной диск и внешние диски, исключаем системные
                    if mountpoint == "/" or (
                        not mountpoint.startswith("/System")
                        and not mountpoint.startswith("/private")
                        and not mountpoint.startswith("/dev")
                        and not mountpoint.startswith("/Volumes/com.apple")
                    ):
                        physical_disks.append(disk)
                else:
                    # Для других ОС оставляем текущую логику
                    if not device.startswith(("/dev/loop", "/dev/sr")):
                        physical_disks.append(disk)

            # Если нет физических дисков, показываем все диски
            if not physical_disks and self.system_info["disks"]:
                physical_disks = self.system_info["disks"]

            for disk in physical_disks:
                total_gb = disk["total"] / (1024**3)
                used_gb = disk["used"] / (1024**3)
                free_gb = disk["free"] / (1024**3)

                # Добавляем заголовок диска с информацией о устройстве
                device_name = disk.get("device", "Неизвестно")
                mount_point = disk.get("mountpoint", "Неизвестно")

                # Для macOS используем более понятные имена
                if platform.system() == "Darwin":
                    if mount_point == "/":
                        display_name = "Macintosh HD"
                    elif mount_point.startswith("/Volumes/"):
                        # Извлекаем имя тома из пути
                        volume_name = mount_point.replace("/Volumes/", "")
                        display_name = f"Том: {volume_name}"
                    else:
                        display_name = f"Диск: {device_name}"
                else:
                    display_name = f"Диск: {device_name}"

                disks_rows.append(
                    ft.Text(
                        display_name,
                        weight=ft.FontWeight.BOLD,
                        size=16,
                    )
                )

                # Добавляем информацию о точке монтирования
                disks_rows.append(
                    self.create_info_row("Точка монтирования:", mount_point)
                )

                # Добавляем информацию об использовании
                disks_rows.append(
                    self.create_info_row(
                        "Использование:",
                        f"{used_gb:.1f} ГБ / {total_gb:.1f} ГБ ({disk['percent']}%)",
                    )
                )

                # Добавляем прогресс-бар для диска
                disks_rows.append(
                    ft.ProgressBar(
                        value=disk["percent"] / 100,
                        bgcolor=ft.colors.BLACK12,
                        color=ft.colors.BLUE if disk["percent"] < 90 else ft.colors.RED,
                        height=10,
                    )
                )

                # Добавляем информацию о свободном месте
                disks_rows.append(
                    self.create_info_row("Свободно:", f"{free_gb:.1f} ГБ")
                )

                # Добавляем информацию о файловой системе, если доступна
                if "fstype" in disk:
                    disks_rows.append(
                        self.create_info_row("Файловая система:", disk["fstype"])
                    )

                disks_rows.append(ft.Divider())

        # Создаем содержимое для контейнера
        content_controls = [
            ft.Text(
                "Диски",
                weight=ft.FontWeight.BOLD,
                size=18,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Divider(),
        ]

        # Добавляем строки с информацией о дисках или сообщение об отсутствии информации
        if disks_rows:
            content_controls.extend(disks_rows)
        else:
            content_controls.append(ft.Text("Информация о дисках недоступна"))

        return ft.Container(
            content=ft.Column(
                content_controls,
                spacing=10,
            ),
            padding=15,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
        )

    def create_uptime_info(self):
        """Создание контейнера с информацией о времени работы"""
        uptime_seconds = self.system_info["uptime"]

        # Создаем строку с временем работы
        self.uptime_row = self.create_info_row(
            "Система работает:", self.format_uptime(uptime_seconds)
        )

        uptime_info = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Время работы",
                        weight=ft.FontWeight.BOLD,
                        size=18,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Divider(),
                    self.uptime_row,
                ],
                spacing=10,
            ),
            padding=15,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
        )

        return uptime_info

    def start_uptime_timer(self):
        """Запуск таймера для обновления времени работы"""
        self.uptime_timer_running = True
        self.uptime_timer = threading.Thread(target=self.update_uptime_loop)
        self.uptime_timer.daemon = True
        self.uptime_timer.start()

    def stop_uptime_timer(self):
        """Остановка таймера"""
        self.uptime_timer_running = False
        if self.uptime_timer:
            self.uptime_timer.join(timeout=1)

    def update_uptime_loop(self):
        """Цикл обновления времени работы"""
        while self.uptime_timer_running:
            try:
                # Получаем текущее время работы
                boot_time = psutil.boot_time()
                uptime_seconds = time.time() - boot_time

                # Обновляем текст времени работы, если строка существует
                if (
                    hasattr(self, "uptime_row")
                    and self.uptime_row
                    and len(self.uptime_row.controls) > 1
                ):
                    self.uptime_row.controls[1].value = self.format_uptime(
                        uptime_seconds
                    )
                    self.update()
            except Exception as e:
                print(f"Ошибка при обновлении времени работы: {e}")

            # Ждем 1 секунду перед следующим обновлением
            time.sleep(1)

    def format_uptime(self, seconds):
        """Форматирование времени работы"""
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        if days > 0:
            return f"{int(days)} дн. {int(hours)} ч. {int(minutes)} мин. {int(seconds)} сек."
        elif hours > 0:
            return f"{int(hours)} ч. {int(minutes)} мин. {int(seconds)} сек."
        elif minutes > 0:
            return f"{int(minutes)} мин. {int(seconds)} сек."
        else:
            return f"{int(seconds)} сек."
