import flet as ft
from modules.ui.components.process_table import (
    ProcessTable,
    sort_processes,
    _sort_column,
    _sort_ascending,
)
from modules.config.settings import TABLE_SETTINGS
from modules.system.process_monitor import ProcessMonitor


class ProcessesView(ft.Container):
    def __init__(self, process_monitor):
        super().__init__()
        self.process_monitor = process_monitor
        self.processes = []
        self.search_text = ""
        self.process_table = None
        self.loading = True

        # Создаем поле поиска
        self.search_field = ft.TextField(
            hint_text="Поиск процессов...",
            prefix_icon=ft.icons.SEARCH,
            on_change=self.handle_search,
            expand=True,
            height=40,
            border_radius=20,
        )

        # Создаем индикатор загрузки
        loading_indicator = ft.ProgressRing()

        # Создаем контейнер для таблицы процессов с прокруткой
        self.process_table_container = ft.Container(
            content=loading_indicator,
            expand=True,  # Позволяем контейнеру расширяться
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
            padding=TABLE_SETTINGS["padding"],
        )

        # Настраиваем контейнер с прокруткой через Column
        self.content = ft.Column(
            [
                ft.Text(
                    "Процессы (показаны топ-50 по использованию памяти)",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                self.search_field,
                self.process_table_container,
            ],
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,  # Включаем прокрутку на Column, а не на Container
            expand=True,  # Позволяем колонке расширяться
        )
        self.padding = 20
        self.expand = True
        self.alignment = ft.alignment.center

    def did_mount(self):
        # Регистрируем callback для обновления UI
        self.process_monitor.register_callback(self.update_processes)
        # Запускаем мониторинг процессов
        self.process_monitor.start_monitoring()

    def will_unmount(self):
        # Отменяем регистрацию callback при удалении компонента
        self.process_monitor.unregister_callback(self.update_processes)

    def update_processes(self, processes):
        """Обновление списка процессов - теперь не асинхронная функция"""
        self.processes = processes
        self.loading = False

        # Применяем фильтр поиска
        from modules.utils.process_manager import ProcessManager

        filtered_processes = ProcessManager.filter_processes(
            self.processes, self.search_text
        )

        # Обновляем таблицу
        self.process_table_container.content = ProcessTable(
            filtered_processes, on_kill=self.kill_process
        )
        self.update()

    def kill_process(self, pid):
        """Завершение процесса"""
        return self.process_monitor.kill_process(pid)

    def handle_search(self, e):
        """Обработка поиска"""
        self.search_text = e.control.value

        # Фильтруем процессы
        from modules.utils.process_manager import ProcessManager

        filtered_processes = ProcessManager.filter_processes(
            self.processes, self.search_text
        )

        # Применяем сохраненную сортировку к отфильтрованным процессам
        if _sort_column is not None:
            filtered_processes = sort_processes(
                filtered_processes, _sort_column, _sort_ascending
            )

        # Обновляем таблицу
        self.process_table_container.content = ProcessTable(
            filtered_processes, on_kill=self.kill_process
        )
        self.update()
