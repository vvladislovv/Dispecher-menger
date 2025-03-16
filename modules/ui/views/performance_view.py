import flet as ft
import random


def PerformanceView():
    def create_chart(color, height):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        width=5,
                        height=random.randint(20, height),
                        bgcolor=color,
                        border_radius=5,
                        tooltip=f"{random.randint(0, 100)}%",
                    )
                    for _ in range(20)
                ],
                spacing=5,
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.END,
            ),
            height=height,
            border_radius=10,
            padding=10,
            bgcolor=ft.colors.BLACK12,
        )

    def create_metric_card(title, value, chart_color, chart_height=150):
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
                    create_chart(chart_color, chart_height),
                ],
            ),
            padding=15,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
        )

    def create_disk_card(disk_name, used, total, used_percent):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(disk_name, size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(
                                f"{used} / {total}", size=16, weight=ft.FontWeight.BOLD
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=10),
                    ft.ProgressBar(
                        value=used_percent / 100,
                        bgcolor=ft.colors.BLACK12,
                        color=ft.colors.BLUE if used_percent < 90 else ft.colors.RED,
                        height=20,
                        tooltip=f"{used_percent}%",
                    ),
                ],
            ),
            padding=15,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
        )

    return ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Производительность",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=20),
                ft.Row(
                    [
                        ft.Container(
                            content=create_metric_card(
                                "Загрузка ЦП",
                                "45%",
                                ft.colors.BLUE,
                            ),
                            expand=True,
                        ),
                        ft.Container(width=20),
                        ft.Container(
                            content=create_metric_card(
                                "Использование памяти",
                                "8.5 ГБ / 16 ГБ",
                                ft.colors.GREEN,
                            ),
                            expand=True,
                        ),
                    ],
                ),
                ft.Container(height=20),
                ft.Text(
                    "Диски",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(height=10),
                create_disk_card("Диск C:", "120 ГБ", "256 ГБ", 47),
                ft.Container(height=10),
                create_disk_card("Диск D:", "890 ГБ", "1 ТБ", 89),
                ft.Container(height=10),
                create_disk_card("Диск E:", "1.8 ТБ", "2 ТБ", 90),
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=20,
        expand=True,
    )
