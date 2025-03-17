import flet as ft
import datetime
from modules.database.db_service import get_db_service
from modules.utils.logger import get_logger

# Инициализация логгера и сервиса БД
logger = get_logger()
db_service = get_db_service()


class HistoryView(ft.Container):
    def __init__(self):
        super().__init__()
        self.db_service = db_service
        self.logs_table = None
        self.processes_table = None
        self.current_tab = "logs"  # По умолчанию показываем логи

        # Инициализируем содержимое
        self.content = self.build()

    def build(self):
        logger.info("Инициализация представления истории")

        # Создаем таблицу для логов
        self.logs_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Время")),
                ft.DataColumn(ft.Text("Уровень")),
                ft.DataColumn(ft.Text("Источник")),
                ft.DataColumn(ft.Text("Сообщение")),
            ],
            rows=[],
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, ft.colors.OUTLINE),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.OUTLINE),
            sort_column_index=0,
            sort_ascending=False,
        )

        # Создаем таблицу для завершенных процессов
        self.processes_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Время")),
                ft.DataColumn(ft.Text("Имя процесса")),
                ft.DataColumn(ft.Text("PID")),
                ft.DataColumn(ft.Text("Память (МБ)")),
                ft.DataColumn(ft.Text("CPU %")),
                ft.DataColumn(ft.Text("Статус")),
                ft.DataColumn(ft.Text("Завершен")),
            ],
            rows=[],
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, ft.colors.OUTLINE),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.OUTLINE),
            sort_column_index=0,
            sort_ascending=False,
        )

        # Создаем фильтры для логов
        log_level_dropdown = ft.Dropdown(
            label="Уровень логов",
            options=[
                ft.dropdown.Option("Все"),
                ft.dropdown.Option("INFO"),
                ft.dropdown.Option("WARNING"),
                ft.dropdown.Option("ERROR"),
                ft.dropdown.Option("DEBUG"),
            ],
            value="Все",
            on_change=lambda e: self.load_logs(
                level=None if e.control.value == "Все" else e.control.value
            ),
        )

        # Создаем кнопки для переключения между логами и процессами
        logs_tab = ft.ElevatedButton(
            text="Логи",
            icon=ft.icons.LIST_ALT,
            on_click=lambda e: self.show_logs(),
            bgcolor=(
                ft.colors.PRIMARY
                if self.current_tab == "logs"
                else ft.colors.SURFACE_VARIANT
            ),
        )

        processes_tab = ft.ElevatedButton(
            text="Завершенные процессы",
            icon=ft.icons.STOP_CIRCLE,
            on_click=lambda e: self.show_processes(),
            bgcolor=(
                ft.colors.PRIMARY
                if self.current_tab == "processes"
                else ft.colors.SURFACE_VARIANT
            ),
        )

        # Кнопка обновления
        refresh_button = ft.IconButton(
            icon=ft.icons.REFRESH,
            tooltip="Обновить",
            on_click=lambda e: self.refresh_data(),
        )

        # Создаем контейнер для текущей таблицы
        self.table_container = ft.Container(
            content=(
                self.logs_table if self.current_tab == "logs" else self.processes_table
            ),
            padding=10,
            expand=True,
        )

        # Загружаем данные
        self.load_logs()
        self.load_processes()

        # Возвращаем основной контейнер
        return ft.Column(
            [
                ft.Text("История", size=24, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        logs_tab,
                        processes_tab,
                        ft.Container(expand=True),
                        log_level_dropdown,
                        refresh_button,
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                self.table_container,
            ],
            expand=True,
        )

    def show_logs(self):
        """Показывает таблицу логов"""
        logger.debug("Переключение на вкладку логов")
        self.current_tab = "logs"
        self.table_container.content = self.logs_table
        self.update()

    def show_processes(self):
        """Показывает таблицу завершенных процессов"""
        logger.debug("Переключение на вкладку завершенных процессов")
        self.current_tab = "processes"
        self.table_container.content = self.processes_table
        self.update()

    def refresh_data(self):
        """Обновляет данные в текущей таблице"""
        logger.info("Обновление данных истории")
        if self.current_tab == "logs":
            self.load_logs()
        else:
            self.load_processes()

    def load_logs(self, level=None, limit=100):
        """Загружает логи из базы данных"""
        logger.debug(
            f"Загрузка логов из базы данных (уровень: {level}, лимит: {limit})"
        )
        try:
            logs = self.db_service.get_logs(limit=limit, level=level)

            # Очищаем таблицу
            self.logs_table.rows.clear()

            # Добавляем строки в таблицу
            for log in logs:
                self.logs_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(
                                ft.Text(log.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
                            ),
                            ft.DataCell(ft.Text(log.level)),
                            ft.DataCell(ft.Text(log.source)),
                            ft.DataCell(ft.Text(log.message)),
                        ]
                    )
                )

            # Обновляем таблицу
            self.update()
            logger.debug(f"Загружено {len(logs)} логов")
        except Exception as e:
            logger.exception(e, "Ошибка при загрузке логов:")

    def load_processes(self, limit=100):
        """Загружает информацию о завершенных процессах из базы данных"""
        logger.debug(f"Загрузка завершенных процессов из базы данных (лимит: {limit})")
        try:
            processes = self.db_service.get_terminated_processes(limit=limit)

            # Очищаем таблицу
            self.processes_table.rows.clear()

            # Добавляем строки в таблицу
            for process in processes:
                self.processes_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(
                                ft.Text(process.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
                            ),
                            ft.DataCell(ft.Text(process.process_name)),
                            ft.DataCell(ft.Text(process.pid)),
                            ft.DataCell(ft.Text(f"{process.memory_usage:.2f}")),
                            ft.DataCell(ft.Text(f"{process.cpu_usage:.1f}%")),
                            ft.DataCell(ft.Text(process.status)),
                            ft.DataCell(ft.Text(process.terminated_by)),
                        ]
                    )
                )

            # Обновляем таблицу
            self.update()
            logger.debug(f"Загружено {len(processes)} завершенных процессов")
        except Exception as e:
            logger.exception(e, "Ошибка при загрузке завершенных процессов:")
