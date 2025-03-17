import flet as ft
from modules.utils.process_manager import ProcessManager

# Глобальные переменные для сохранения состояния сортировки
_sort_column = None
_sort_ascending = True


def sort_processes(processes, column, ascending=True):
    """Сортировка процессов по указанному столбцу"""
    if column == 0:  # Имя
        return sorted(processes, key=lambda x: x[0].lower(), reverse=not ascending)
    elif column == 1:  # PID
        return sorted(processes, key=lambda x: int(x[1]), reverse=not ascending)
    elif column == 2:  # Память
        return sorted(processes, key=lambda x: float(x[2]), reverse=not ascending)
    elif column == 3:  # CPU
        return sorted(processes, key=lambda x: float(x[3]), reverse=not ascending)
    elif column == 4:  # Статус
        return sorted(processes, key=lambda x: x[4], reverse=not ascending)
    return processes


def kill_process(e, pid):
    """
    Обработчик нажатия на кнопку завершения процесса.

    Аргументы:
        e (ControlEvent): Событие нажатия на кнопку
        pid (str): Идентификатор процесса для завершения

    Действия:
        1. Получает функцию обратного вызова из свойств кнопки
        2. Вызывает функцию обратного вызова с передачей PID процесса
        3. Обработка ошибок и логирование
    """
    try:
        # Получаем функцию обратного вызова из свойств кнопки
        on_kill = e.control.data

        # Вызываем функцию обратного вызова
        if on_kill:
            success = on_kill(pid)

            # Не вызываем update() для кнопки, так как она будет обновлена вместе с таблицей
            # e.control.update()  # Удаляем эту строку, которая вызывает ошибку

            # Если нужно показать результат, можно использовать диалоговое окно или снэкбар
            if not success:
                # Здесь можно показать сообщение об ошибке, если нужно
                pass
    except Exception as e:
        import traceback

        print(f"Ошибка при завершении процесса: {str(e)}")
        print(traceback.format_exc())


def ProcessTable(processes, on_kill=None):
    """Создает таблицу процессов"""
    global _sort_column, _sort_ascending

    # Создаем таблицу
    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Имя"), on_sort=lambda e: handle_sort(e, 0)),
            ft.DataColumn(ft.Text("PID"), on_sort=lambda e: handle_sort(e, 1)),
            ft.DataColumn(ft.Text("Память (МБ)"), on_sort=lambda e: handle_sort(e, 2)),
            ft.DataColumn(ft.Text("CPU %"), on_sort=lambda e: handle_sort(e, 3)),
            ft.DataColumn(ft.Text("Статус"), on_sort=lambda e: handle_sort(e, 4)),
            ft.DataColumn(ft.Text("Действия")),
        ],
        rows=[],
        sort_column_index=_sort_column,
        sort_ascending=_sort_ascending,
        heading_row_height=35,
        data_row_min_height=35,
        data_row_max_height=50,
        border=ft.border.all(1, ft.colors.OUTLINE),
        border_radius=10,
        vertical_lines=ft.border.BorderSide(1, ft.colors.OUTLINE),
        horizontal_lines=ft.border.BorderSide(1, ft.colors.OUTLINE),
        column_spacing=10,
    )

    # Добавляем строки в таблицу
    for process in processes:
        name, pid, memory, cpu, status = process

        # Создаем кнопку завершения процесса
        kill_button = ft.IconButton(
            icon=ft.icons.CLOSE,
            tooltip="Завершить процесс",
            icon_color=ft.colors.RED_400,
            data=on_kill,  # Сохраняем функцию обратного вызова в свойствах кнопки
            on_click=lambda e, pid=pid: kill_process(e, pid),
        )

        table.rows.append(
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

    # Функция для обработки сортировки
    def handle_sort(e, column_index):
        global _sort_column, _sort_ascending

        # Если нажали на тот же столбец, меняем направление сортировки
        if _sort_column == column_index:
            _sort_ascending = not _sort_ascending
        else:
            _sort_column = column_index
            _sort_ascending = True

        # Обновляем состояние сортировки в таблице
        table.sort_column_index = _sort_column
        table.sort_ascending = _sort_ascending

        # Сортируем процессы
        sorted_processes = sort_processes(processes, _sort_column, _sort_ascending)

        # Очищаем таблицу
        table.rows.clear()

        # Добавляем отсортированные строки
        for process in sorted_processes:
            name, pid, memory, cpu, status = process

            # Создаем кнопку завершения процесса
            kill_button = ft.IconButton(
                icon=ft.icons.CLOSE,
                tooltip="Завершить процесс",
                icon_color=ft.colors.RED_400,
                data=on_kill,
                on_click=lambda e, pid=pid: kill_process(e, pid),
            )

            table.rows.append(
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

        # Обновляем таблицу
        table.update()

    return table
