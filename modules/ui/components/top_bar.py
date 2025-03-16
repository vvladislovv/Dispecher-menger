import flet as ft


def TopBar():
    theme_icon = ft.IconButton(
        icon=ft.icons.LIGHT_MODE,
        tooltip="Сменить тему",
        on_click=lambda e: toggle_theme(e, theme_icon),
    )

    search_field = ft.TextField(
        hint_text="Поиск...",
        prefix_icon=ft.icons.SEARCH,
        expand=True,
        height=40,
        border_radius=20,
    )

    return ft.Container(
        content=ft.Row(
            [search_field, theme_icon],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.padding.only(left=20, right=20, top=10, bottom=10),
        bgcolor=ft.colors.SURFACE_VARIANT,
    )


def toggle_theme(e, theme_icon):
    page = e.page
    page.theme_mode = (
        ft.ThemeMode.DARK
        if page.theme_mode == ft.ThemeMode.LIGHT
        else ft.ThemeMode.LIGHT
    )
    theme_icon.icon = (
        ft.icons.DARK_MODE
        if page.theme_mode == ft.ThemeMode.LIGHT
        else ft.icons.LIGHT_MODE
    )
    page.update()
