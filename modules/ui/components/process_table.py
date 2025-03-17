import flet as ft
from modules.utils.process_manager import ProcessManager

# Глобальные переменные для хранения состояния сортировки
_sort_column = None
_sort_ascending = True


def ProcessTable(processes, on_kill=None):
    """Функция для создания таблицы процессов с возможностью сортировки"""
    # Используем глобальные переменные для сохранения состояния сортировки
    global _sort_column, _sort_ascending

    # Сохраняем исходные данные для сортировки
    current_processes = processes.copy()

    # Если уже была установлена сортировка, применяем её
    if _sort_column is not None:
        current_processes = sort_processes(
            current_processes, _sort_column, _sort_ascending
        )

    # Функция для создания строк таблицы
    def create_rows(processes_list):
        rows = []
        for process in processes_list:
            name, pid, memory, cpu, status = process

            # Создаем кнопку завершения процесса
            kill_button = ft.IconButton(
                icon=ft.icons.CLOSE,
                icon_color=ft.colors.RED,
                tooltip="Завершить процесс",
                on_click=lambda e, pid=pid: kill_process(e, pid),
            )

            # Добавляем строку
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(name)),
                        ft.DataCell(ft.Text(pid)),
                        ft.DataCell(ft.Text(memory)),
                        ft.DataCell(ft.Text(cpu)),
                        ft.DataCell(ft.Text(status)),
                        ft.DataCell(kill_button),
                    ]
                )
            )
        return rows

    # Функция для обработки завершения процесса
    def kill_process(e, pid):
        if on_kill:
            success = on_kill(pid)
            if success:
                e.control.icon_color = ft.colors.GREEN
                e.control.tooltip = "Процесс завершен"
            else:
                e.control.icon_color = ft.colors.AMBER
                e.control.tooltip = "Не удалось завершить процесс"
            e.control.update()

    # Функция для сортировки данных
    def sort_data(e, column_index, table):
        global _sort_column, _sort_ascending

        # Если нажали на тот же столбец, меняем порядок сортировки
        if _sort_column == column_index:
            _sort_ascending = not _sort_ascending
        else:
            _sort_column = column_index
            # По умолчанию для имени - по возрастанию (A-Z)
            # Для числовых столбцов (PID, память, CPU) - по убыванию
            _sort_ascending = column_index == 0

        # Сортируем процессы
        sorted_processes = sort_processes(
            current_processes, _sort_column, _sort_ascending
        )

        # Обновляем строки таблицы
        table.rows = create_rows(sorted_processes)
        table.update()

    # Создаем таблицу
    table = ft.DataTable(
        columns=[
            ft.DataColumn(
                ft.Row(
                    [
                        ft.Text("Имя процесса", weight=ft.FontWeight.BOLD),
                        ft.IconButton(
                            icon=ft.icons.SORT,
                            tooltip="Сортировать по имени",
                            on_click=lambda e: sort_data(e, 0, table),
                        ),
                    ]
                )
            ),
            ft.DataColumn(
                ft.Row(
                    [
                        ft.Text("PID", weight=ft.FontWeight.BOLD),
                        ft.IconButton(
                            icon=ft.icons.SORT,
                            tooltip="Сортировать по PID",
                            on_click=lambda e: sort_data(e, 1, table),
                        ),
                    ]
                )
            ),
            ft.DataColumn(
                ft.Row(
                    [
                        ft.Text("Память (МБ)", weight=ft.FontWeight.BOLD),
                        ft.IconButton(
                            icon=ft.icons.SORT,
                            tooltip="Сортировать по использованию памяти",
                            on_click=lambda e: sort_data(e, 2, table),
                        ),
                    ]
                )
            ),
            ft.DataColumn(
                ft.Row(
                    [
                        ft.Text("CPU (%)", weight=ft.FontWeight.BOLD),
                        ft.IconButton(
                            icon=ft.icons.SORT,
                            tooltip="Сортировать по использованию CPU",
                            on_click=lambda e: sort_data(e, 3, table),
                        ),
                    ]
                )
            ),
            ft.DataColumn(ft.Text("Статус", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Действия", weight=ft.FontWeight.BOLD)),
        ],
        rows=create_rows(current_processes),
        horizontal_lines=ft.border.BorderSide(1, ft.colors.OUTLINE),
        vertical_lines=ft.border.BorderSide(1, ft.colors.OUTLINE),
        border=ft.border.all(1, ft.colors.OUTLINE),
        border_radius=10,
        column_spacing=10,
        heading_row_height=40,
        data_row_min_height=40,
        data_row_max_height=50,
        show_checkbox_column=False,
    )

    return table


def sort_processes(processes, column_index, ascending):
    """Сортировка процессов по указанному столбцу"""
    if column_index is None:
        return processes

    # Функция для преобразования значения в числовой формат для сортировки
    def get_sort_key(process, idx):
        value = process[idx]
        if idx == 0:  # Имя процесса - строка
            return value.lower()
        elif idx == 1:  # PID - число в строковом формате
            return int(value)
        elif idx in [
            2,
            3,
        ]:  # Память и CPU - числа с плавающей точкой в строковом формате
            return float(value.replace("%", ""))
        return value

    # Копируем процессы для сортировки
    sorted_processes = processes.copy()

    # Сортируем процессы
    sorted_processes.sort(
        key=lambda x: get_sort_key(x, column_index),
        reverse=not ascending if column_index == 0 else ascending,
    )

    return sorted_processes
