import flet as ft
import threading
import time
from modules.config.settings import WINDOW_SETTINGS, MONITORING_SETTINGS
from modules.ui.components.top_bar import TopBar
from modules.ui.views.processes_view import ProcessesView
from modules.ui.views.system_info_view import SystemInfoView
from modules.ui.views.performance_view import PerformanceView
from modules.system.process_monitor import ProcessMonitor
from modules.system.performance_monitor import PerformanceMonitor


def SystemMonitorApp(page: ft.Page):
    # Конфигурация страницы
    page.title = WINDOW_SETTINGS["title"]
    page.window.width = WINDOW_SETTINGS["width"]
    page.window.height = WINDOW_SETTINGS["height"]
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.update()

    # Инициализация мониторов
    process_monitor = ProcessMonitor()
    process_monitor.update_interval = MONITORING_SETTINGS["process_update_interval"]

    performance_monitor = PerformanceMonitor(
        history_length=MONITORING_SETTINGS["performance_history_length"]
    )
    performance_monitor.update_interval = MONITORING_SETTINGS[
        "performance_update_interval"
    ]

    # Создаем компоненты
    top_bar = TopBar()
    processes_view = ProcessesView(process_monitor)
    system_info_view = SystemInfoView()
    performance_view = PerformanceView(performance_monitor)

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

        # Плавное изменение прозрачности
        def animate_opacity():
            for i in range(11):
                tabs_content.opacity = i / 10
                tabs_content.update()
                page.update()
                time.sleep(0.02)

        # Запускаем анимацию в отдельном потоке
        threading.Thread(target=animate_opacity, daemon=True).start()

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

    # Функция для обработки обратных вызовов от мониторов
    def process_callbacks():
        try:
            process_monitor.process_callbacks()
            performance_monitor.process_callbacks()
            page.update()
        except Exception as e:
            print(f"Ошибка при обработке обратных вызовов: {e}")

    # Флаг для управления работой таймера
    timer_running = True

    # Функция таймера с более коротким интервалом для более плавного обновления
    def timer_thread():
        while timer_running:
            try:
                # Вызываем обработку обратных вызовов
                process_callbacks()
                time.sleep(0.3)  # Уменьшаем интервал для более плавного обновления
            except Exception as e:
                print(f"Ошибка в таймере: {e}")
                time.sleep(1)  # Пауза при ошибке

    # Запускаем таймер в отдельном потоке ПОСЛЕ добавления элементов на страницу
    timer_thread = threading.Thread(target=timer_thread, daemon=True)
    timer_thread.start()

    # Функция для остановки таймера при закрытии приложения
    def on_close():
        nonlocal timer_running
        timer_running = False
        # Останавливаем мониторы
        process_monitor.stop_monitoring()
        performance_monitor.stop_monitoring()

    # Регистрируем обработчик закрытия
    page.on_close = on_close
