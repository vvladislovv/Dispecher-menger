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
        """
        Завершает процесс с указанным идентификатором (PID).

        Аргументы:
            pid (str): Идентификатор процесса для завершения

        Возвращает:
            bool: True, если процесс успешно завершен, False в противном случае

        Действия:
            1. Находит информацию о процессе в текущем списке процессов
            2. Передает информацию о процессе в метод kill_process монитора процессов
            3. Обновление UI происходит автоматически через callback
        """
        try:
            # Получаем информацию о процессе перед завершением
            process_info = None
            for proc in self.processes:
                if proc[1] == pid:  # Ищем процесс с нужным PID
                    process_info = proc
                    break

            # Завершаем процесс через process_monitor
            # Передаем информацию о процессе, чтобы не записывать ее дважды
            success = self.process_monitor.kill_process(pid, process_info)

            # Обновляем список процессов
            if success:
                # Обновление произойдет автоматически через callback
                pass

            return success
        except Exception as e:
            import traceback

            print(f"Ошибка при завершении процесса: {str(e)}")
            print(traceback.format_exc())
            return False

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

    def terminate_process(self, e, pid):
        """Обработчик нажатия на кнопку завершения процесса"""
        try:
            # Получаем информацию о процессе перед завершением
            process_info = None
            for row in self.process_table.rows:
                if row.cells[1].content.value == pid:  # Ищем строку с нужным PID
                    name = row.cells[0].content.value
                    memory = row.cells[2].content.value
                    cpu = row.cells[3].content.value
                    status = row.cells[4].content.value
                    process_info = [name, pid, memory, cpu, status]
                    break

            # Вызываем метод завершения процесса
            success = self.process_monitor.terminate_process(pid)

            if success:
                # Если процесс успешно завершен, обновляем список процессов
                self.update_processes()

                # Проверяем, что информация о процессе была сохранена в БД
                if process_info:
                    from modules.database.db_service import get_db_service

                    db_service = get_db_service()
                    db_service.add_terminated_process(process_info)
                    print(f"Процесс {name} (PID: {pid}) сохранен в БД")
            else:
                # Если не удалось завершить процесс, показываем сообщение об ошибке
                self.show_error_message(f"Не удалось завершить процесс с PID {pid}")
        except Exception as e:
            import traceback

            print(f"Ошибка при завершении процесса: {str(e)}")
            print(traceback.format_exc())
            self.show_error_message(f"Ошибка при завершении процесса: {str(e)}")
