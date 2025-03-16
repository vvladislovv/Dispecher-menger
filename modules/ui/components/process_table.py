import flet as ft
from modules.utils.process_manager import ProcessManager


def ProcessTable(processes):
    current_processes = processes.copy()
    sort_ascending = True

    def create_kill_button(process_name):
        return ft.IconButton(
            icon=ft.icons.CLOSE,
            icon_color=ft.colors.ERROR,
            icon_size=20,
            tooltip="Завершить процесс",
            on_click=lambda e: show_kill_dialog(e, process_name),
        )

    def show_kill_dialog(e, process_name):
        def close_dlg(e):
            dlg.open = False
            e.page.update()

        def kill_process(e):
            # Здесь будет логика завершения процесса
            close_dlg(e)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                f"Завершить процесс {process_name}?",
                text_align=ft.TextAlign.CENTER,
                weight=ft.FontWeight.BOLD,
            ),
            content=ft.Text(
                "Вы уверены, что хотите завершить этот процесс?",
                text_align=ft.TextAlign.CENTER,
            ),
            actions=[
                ft.TextButton("Отмена", on_click=close_dlg),
                ft.TextButton(
                    "Завершить",
                    on_click=kill_process,
                    style=ft.ButtonStyle(color=ft.colors.ERROR),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        e.page.dialog = dlg
        dlg.open = True
        e.page.update()

    def sort_data(e, column_index, table):
        nonlocal sort_ascending
        sort_ascending = not sort_ascending
        nonlocal current_processes
        current_processes = ProcessManager.sort_processes(
            current_processes, column_index, sort_ascending
        )
        table.rows = create_rows(current_processes)
        e.page.update()

    def create_rows(processes):
        return [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(process[0])),
                    ft.DataCell(ft.Text(process[1])),
                    ft.DataCell(ft.Text(process[2])),
                    ft.DataCell(ft.Text(process[3])),
                    ft.DataCell(ft.Text(process[4])),
                    ft.DataCell(create_kill_button(process[0])),
                ]
            )
            for process in processes
        ]

    table = ft.DataTable(
        columns=[
            ft.DataColumn(
                ft.Row(
                    [
                        ft.Text("Имя процесса"),
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
                        ft.Text("PID"),
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
                        ft.Text("Память (МБ)"),
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
                        ft.Text("CPU %"),
                        ft.IconButton(
                            icon=ft.icons.SORT,
                            tooltip="Сортировать по загрузке CPU",
                            on_click=lambda e: sort_data(e, 3, table),
                        ),
                    ]
                )
            ),
            ft.DataColumn(ft.Text("Статус")),
            ft.DataColumn(ft.Text("Действия")),
        ],
        rows=create_rows(current_processes),
        border=ft.border.all(1, ft.colors.OUTLINE),
        border_radius=10,
        vertical_lines=ft.border.BorderSide(1, ft.colors.OUTLINE),
        horizontal_lines=ft.border.BorderSide(1, ft.colors.OUTLINE),
    )

    return table
