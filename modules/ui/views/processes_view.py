import flet as ft
from modules.ui.components.process_table import ProcessTable
from modules.config.settings import TABLE_SETTINGS


def ProcessesView(processes):
    process_table = ProcessTable(processes)

    return ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Процессы",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(
                    content=ft.Column(
                        [process_table],
                        scroll=ft.ScrollMode.ALWAYS,
                    ),
                    height=TABLE_SETTINGS["height"],
                    border=ft.border.all(1, ft.colors.OUTLINE),
                    border_radius=10,
                    padding=TABLE_SETTINGS["padding"],
                ),
            ],
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=20,
        expand=True,
        alignment=ft.alignment.center,
    )
