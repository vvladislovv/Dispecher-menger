import flet as ft
from modules.system.performance_monitor import PerformanceMonitor


class PerformanceView(ft.Container):
    def __init__(self, performance_monitor):
        super().__init__()
        self.performance_monitor = performance_monitor
        self.performance_data = None
        self.loading = True

        # Создаем индикатор загрузки
        loading_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Загрузка данных о производительности...",
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

        # Создаем контейнеры для графиков
        self.cpu_chart_container = ft.Container(
            content=ft.Text("Загрузка..."),
            height=200,
            border_radius=10,
            padding=10,
            bgcolor=ft.colors.BLACK12,
        )

        self.memory_chart_container = ft.Container(
            content=ft.Text("Загрузка..."),
            height=200,
            border_radius=10,
            padding=10,
            bgcolor=ft.colors.BLACK12,
        )

        self.disk_chart_container = ft.Container(
            content=ft.Text("Загрузка..."),
            height=200,
            border_radius=10,
            padding=10,
            bgcolor=ft.colors.BLACK12,
        )

        self.network_chart_container = ft.Container(
            content=ft.Text("Загрузка..."),
            height=200,
            border_radius=10,
            padding=10,
            bgcolor=ft.colors.BLACK12,
        )

        # Создаем контейнеры для метрик
        self.cpu_metric = self.create_metric_card(
            "Загрузка ЦП", "0%", ft.colors.BLUE, self.cpu_chart_container
        )
        self.memory_metric = self.create_metric_card(
            "Использование памяти",
            "0 ГБ / 0 ГБ",
            ft.colors.GREEN,
            self.memory_chart_container,
        )
        self.disk_metric = self.create_metric_card(
            "Активность диска",
            "0 МБ/с чтение, 0 МБ/с запись",
            ft.colors.ORANGE,
            self.disk_chart_container,
        )
        self.network_metric = self.create_metric_card(
            "Сетевая активность",
            "0 МБ/с отправка, 0 МБ/с получение",
            ft.colors.PURPLE,
            self.network_chart_container,
        )

        # Настраиваем контейнер с улучшенной прокруткой через Column
        self.content = ft.Column(
            [
                ft.Text(
                    "Производительность",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=20),
                (
                    loading_container
                    if self.loading
                    else ft.ListView(
                        [
                            self.cpu_metric,
                            ft.Container(height=20),
                            self.memory_metric,
                            ft.Container(height=20),
                            self.disk_metric,
                            ft.Container(height=20),
                            self.network_metric,
                        ],
                        spacing=10,
                        expand=True,
                    )
                ),
            ],
            expand=True,
        )
        self.padding = 20
        self.expand = True

    def did_mount(self):
        # Регистрируем callback для обновления UI
        self.performance_monitor.register_callback(self.update_performance)
        # Запускаем мониторинг производительности
        self.performance_monitor.start_monitoring()

    def will_unmount(self):
        # Отменяем регистрацию callback при удалении компонента
        self.performance_monitor.unregister_callback(self.update_performance)

    def update_performance(self, performance_data):
        """Обновление данных о производительности - теперь не асинхронная функция"""
        # Сохраняем предыдущее состояние загрузки
        was_loading = self.loading

        # Обновляем данные
        self.performance_data = performance_data
        self.loading = False

        # Обновляем CPU
        cpu_percent = performance_data["cpu"]["current"]
        cpu_history = performance_data["cpu"]["history"]
        self.update_cpu_chart(cpu_percent, cpu_history)

        # Обновляем память
        memory_percent = performance_data["memory"]["current"]
        memory_total = performance_data["memory"]["total"]
        memory_used = performance_data["memory"]["used"]
        memory_history = performance_data["memory"]["history"]
        self.update_memory_chart(
            memory_percent, memory_total, memory_used, memory_history
        )

        # Обновляем диск
        disk_io_current = performance_data["disk_io"]["current"]
        disk_io_history = performance_data["disk_io"]["history"]
        self.update_disk_chart(disk_io_current, disk_io_history)

        # Обновляем сеть
        network_current = performance_data["network"]["current"]
        network_history = performance_data["network"]["history"]
        self.update_network_chart(network_current, network_history)

        # Вместо полной замены контента, обновляем только содержимое существующих контейнеров
        # Это позволит сохранить позицию прокрутки
        if (
            was_loading
            or not hasattr(self, "content")
            or not isinstance(self.content, ft.Column)
        ):
            # Если был загрузка или контент еще не инициализирован, создаем его
            self.content = ft.Column(
                [
                    ft.Text(
                        "Производительность",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=20),
                    ft.ListView(
                        [
                            self.cpu_metric,
                            ft.Container(height=20),
                            self.memory_metric,
                            ft.Container(height=20),
                            self.disk_metric,
                            ft.Container(height=20),
                            self.network_metric,
                        ],
                        spacing=10,
                        expand=True,
                    ),
                ],
                expand=True,
            )
        # Иначе просто обновляем существующий контент
        # Не нужно ничего делать, так как мы уже обновили все метрики и графики выше

        # Обновляем UI
        self.update()

    def create_metric_card(self, title, value, chart_color, chart_container):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(
                                value,
                                size=16,
                                color=chart_color,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=10),
                    chart_container,
                ],
            ),
            padding=15,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
        )

    def update_cpu_chart(self, cpu_percent, cpu_history):
        """Обновление графика CPU"""
        # Обновляем значение
        self.cpu_metric.content.controls[0].controls[1].value = f"{cpu_percent:.1f}%"

        # Обновляем график
        chart = self.create_chart(cpu_history, ft.colors.BLUE, 200, single_value=True)
        self.cpu_chart_container.content = chart

    def update_memory_chart(
        self, memory_percent, memory_total, memory_used, memory_history
    ):
        """Обновление графика памяти"""
        # Обновляем значение
        used_gb = memory_used / (1024**3)
        total_gb = memory_total / (1024**3)
        self.memory_metric.content.controls[0].controls[
            1
        ].value = f"{used_gb:.1f} ГБ / {total_gb:.1f} ГБ ({memory_percent:.1f}%)"

        # Обновляем график
        chart = self.create_chart(
            memory_history, ft.colors.GREEN, 200, single_value=True
        )
        self.memory_chart_container.content = chart

    def update_disk_chart(self, disk_io_current, disk_io_history):
        """Обновление графика диска"""
        # Обновляем значение
        read_speed, write_speed = disk_io_current
        self.disk_metric.content.controls[0].controls[
            1
        ].value = f"{read_speed:.1f} МБ/с чтение, {write_speed:.1f} МБ/с запись"

        # Обновляем график
        chart = self.create_chart(
            disk_io_history, ft.colors.ORANGE, 200, single_value=False
        )
        self.disk_chart_container.content = chart

    def update_network_chart(self, network_current, network_history):
        """Обновление графика сети"""
        # Обновляем значение
        sent_speed, recv_speed = network_current
        self.network_metric.content.controls[0].controls[
            1
        ].value = f"{sent_speed:.1f} МБ/с отправка, {recv_speed:.1f} МБ/с получение"

        # Обновляем график
        chart = self.create_chart(
            network_history, ft.colors.PURPLE, 200, single_value=False
        )
        self.network_chart_container.content = chart

    def create_chart(self, data, color, height, single_value=True):
        """Создание графика"""
        if not data:
            return ft.Text("Нет данных")

        if single_value:
            # Для CPU и памяти (один показатель)
            bars = [
                ft.Container(
                    width=5,
                    height=max(5, value / 100 * height),
                    bgcolor=color,
                    border_radius=5,
                    tooltip=f"{value:.1f}%",
                )
                for value in data
            ]
        else:
            # Для диска и сети (два показателя)
            max_value = max([max(read, write) for read, write in data]) if data else 1
            max_value = max(max_value, 0.1)  # Избегаем деления на ноль

            bars = []
            for read, write in data:
                read_height = max(5, read / max_value * height * 0.8)
                write_height = max(5, write / max_value * height * 0.8)

                bars.append(
                    ft.Row(
                        [
                            ft.Container(
                                width=2,
                                height=read_height,
                                bgcolor=color,
                                border_radius=5,
                                tooltip=f"Чтение: {read:.1f} МБ/с",
                            ),
                            ft.Container(
                                width=2,
                                height=write_height,
                                bgcolor=ft.colors.RED,
                                border_radius=5,
                                tooltip=f"Запись: {write:.1f} МБ/с",
                            ),
                        ],
                        spacing=1,
                        alignment=ft.MainAxisAlignment.CENTER,
                    )
                )

        return ft.Container(
            content=ft.Row(
                bars,
                spacing=2,
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.END,
            ),
            height=height,
            border_radius=10,
            padding=10,
            bgcolor=ft.colors.BLACK12,
        )

    def update_performance_data(self):
        """
        Обновляет данные о производительности системы и графики.

        Действия:
            1. Получает актуальные данные о производительности системы
            2. Обновляет значения в интерфейсе (CPU, память, диски, сеть)
            3. Добавляет новые точки на графики
            4. Обновляет UI
        """
        # Код метода...

    def update_charts(self, data):
        """
        Обновляет графики с новыми данными о производительности.

        Аргументы:
            data (dict): Словарь с данными о производительности системы

        Действия:
            1. Добавляет новые точки на графики CPU и памяти
            2. Удаляет старые точки, если их больше максимального количества
            3. Обновляет графики
        """
        # Код метода...
