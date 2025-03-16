import flet as ft
import asyncio
from modules.config.settings import WINDOW_SETTINGS, TEST_PROCESSES
from modules.ui.components.top_bar import TopBar
from modules.ui.views.processes_view import ProcessesView
from modules.ui.views.system_info_view import SystemInfoView
from modules.ui.views.performance_view import PerformanceView


def SystemMonitorApp(page: ft.Page):
    # Конфигурация страницы
    page.title = WINDOW_SETTINGS["title"]
    page.window.width = WINDOW_SETTINGS["width"]
    page.window.height = WINDOW_SETTINGS["height"]
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.update()

    # Создаем компоненты
    top_bar = TopBar()
    processes_view = ProcessesView(TEST_PROCESSES)
    system_info_view = SystemInfoView()
    performance_view = PerformanceView()

    # Контейнер для содержимого вкладок
    tabs_content = ft.Container(
        content=processes_view,
        expand=True,
        animate_opacity=300,
    )

    def handle_tab_change(e):
        if e.control.selected_index == 0:
            tabs_content.content = processes_view
        elif e.control.selected_index == 1:
            tabs_content.content = system_info_view
        else:
            tabs_content.content = performance_view

        # Анимация смены вкладки
        tabs_content.opacity = 0
        tabs_content.update()

        async def animate_opacity():
            for i in range(11):
                await asyncio.sleep(0.02 * i)
                tabs_content.opacity = i / 10
                tabs_content.update()

        asyncio.run(animate_opacity())

    # Создание навигации
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="Процессы", icon=ft.icons.LIST_ALT),
            ft.Tab(text="О системе", icon=ft.icons.MEMORY),
            ft.Tab(text="Графики", icon=ft.icons.SHOW_CHART),
        ],
        on_change=handle_tab_change,
    )

    # Добавление элементов на страницу
    page.add(
        ft.Column(
            [
                top_bar,
                ft.Container(
                    content=tabs,
                    padding=ft.padding.only(left=20, right=20),
                    bgcolor=ft.colors.SURFACE_VARIANT,
                ),
                tabs_content,
            ],
            expand=True,
        )
    )
