import flet as ft


def SystemInfoView():
    def create_info_row(label, value):
        return ft.Row(
            [
                ft.Text(label, weight=ft.FontWeight.BOLD),
                ft.Text(value),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def create_disks_info():
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Диски",
                        weight=ft.FontWeight.BOLD,
                        size=18,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Divider(),
                    create_info_row("Диск C:", "250 ГБ / 500 ГБ"),
                    create_info_row("Диск D:", "400 ГБ / 1 ТБ"),
                ],
                spacing=10,
            ),
            padding=15,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
        )

    return ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "О системе",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "Общая информация",
                                weight=ft.FontWeight.BOLD,
                                size=18,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Divider(),
                            create_info_row(
                                "Операционная система:", "Windows 10 Pro 64-bit"
                            ),
                            create_info_row(
                                "Процессор:", "Intel Core i7-11700K @ 3.60GHz"
                            ),
                            create_info_row("Память:", "32 ГБ DDR4"),
                            create_info_row("Видеокарта:", "NVIDIA GeForce RTX 3070"),
                            create_info_row(
                                "Материнская плата:", "ASUS ROG STRIX B560-F GAMING"
                            ),
                            create_info_row("Время работы:", "5 часов 23 минуты"),
                        ],
                        spacing=10,
                    ),
                    padding=15,
                    border=ft.border.all(1, ft.colors.OUTLINE),
                    border_radius=10,
                    margin=ft.margin.only(bottom=20),
                ),
                create_disks_info(),
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=20,
        expand=True,
        alignment=ft.alignment.center,
    )
