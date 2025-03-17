import flet as ft
import threading
import time
from modules.config.settings import WINDOW_SETTINGS, MONITORING_SETTINGS
from modules.ui.views.processes_view import ProcessesView
from modules.ui.views.system_info_view import SystemInfoView
from modules.ui.views.performance_view import PerformanceView
from modules.system.process_monitor import ProcessMonitor
from modules.system.performance_monitor import PerformanceMonitor
from modules.utils.logger import get_logger

# Инициализация логгера
logger = get_logger()


def SystemMonitorApp(page: ft.Page):
    logger.info("Запуск приложения SystemMonitorApp")

    # Конфигурация страницы
    page.title = WINDOW_SETTINGS["title"]
    page.window.width = WINDOW_SETTINGS["width"]
    page.window.height = WINDOW_SETTINGS["height"]
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    logger.debug("Настройки страницы применены")
    page.update()

    # Создаем область для логов
    log_area = ft.TextField(
        multiline=True,
        read_only=True,
        min_lines=10,
        max_lines=15,
        value="Логи приложения:\n",
        text_size=12,
        expand=True,
        visible=False,  # По умолчанию скрыта
    )

    # Настройка отображения логов в интерфейсе
    def show_log_in_ui(message):
        log_area.value += message + "\n"
        # Ограничиваем количество строк в логе
        lines = log_area.value.split("\n")
        if len(lines) > 100:  # Оставляем только последние 100 строк
            log_area.value = "\n".join(lines[-100:])
        page.update(log_area)

    # Устанавливаем функцию обратного вызова для логгера
    logger.set_chat_callback(show_log_in_ui)
    logger.info("Логгер настроен для отображения в интерфейсе")

    # Инициализация мониторов
    logger.info("Инициализация мониторов")
    process_monitor = ProcessMonitor()
    process_monitor.update_interval = MONITORING_SETTINGS["process_update_interval"]
    logger.debug(
        f"Интервал обновления процессов: {process_monitor.update_interval} сек"
    )

    performance_monitor = PerformanceMonitor(
        history_length=MONITORING_SETTINGS["performance_history_length"]
    )
    performance_monitor.update_interval = MONITORING_SETTINGS[
        "performance_update_interval"
    ]
    logger.debug(
        f"Интервал обновления производительности: {performance_monitor.update_interval} сек"
    )

    # Создаем компоненты
    logger.info("Создание компонентов интерфейса")
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
        logger.info(f"Переключение на вкладку: {e.control.selected_index}")
        if e.control.selected_index == 0:
            tabs_content.content = processes_view
            logger.debug("Активирована вкладка 'Процессы'")
        elif e.control.selected_index == 1:
            tabs_content.content = system_info_view
            logger.debug("Активирована вкладка 'О системе'")
        else:
            tabs_content.content = performance_view
            logger.debug("Активирована вкладка 'Графики'")

        # Анимация смены вкладки
        tabs_content.opacity = 0
        tabs_content.update()

        # Плавное изменение прозрачности
        def animate_opacity():
            try:
                for i in range(11):
                    tabs_content.opacity = i / 10
                    tabs_content.update()
                    page.update()
                    time.sleep(0.02)
                logger.debug("Анимация смены вкладки завершена")
            except Exception as e:
                logger.exception(e, "Ошибка при анимации смены вкладки:")

        # Запускаем анимацию в отдельном потоке
        threading.Thread(target=animate_opacity, daemon=True).start()

    # Кнопка для отображения/скрытия логов
    toggle_logs_button = ft.IconButton(
        icon=ft.icons.ARTICLE_OUTLINED,
        tooltip="Показать/скрыть логи",
        on_click=lambda e: toggle_logs(),
    )

    # Кнопка для переключения темы
    theme_button = ft.IconButton(
        icon=ft.icons.DARK_MODE,
        tooltip="Сменить тему",
        on_click=lambda e: toggle_theme(),
    )

    def toggle_theme():
        """Переключает тему приложения между светлой и темной"""
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
            theme_button.icon = ft.icons.LIGHT_MODE
            logger.info("Включена темная тема")
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            theme_button.icon = ft.icons.DARK_MODE
            logger.info("Включена светлая тема")
        page.update()

    def toggle_logs():
        log_area.visible = not log_area.visible

        # Если логи становятся видимыми, увеличиваем их размер
        if log_area.visible:
            log_area.min_lines = 10
            log_area.max_lines = 15
            log_area.height = 250  # Устанавливаем фиксированную высоту в пикселях
        else:
            # Если скрываем, можно уменьшить размер для экономии ресурсов
            log_area.min_lines = 5
            log_area.max_lines = 5
            log_area.height = None

        logger.debug(f"Видимость логов изменена: {log_area.visible}")
        page.update(log_area)

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
    logger.info("Добавление элементов на страницу")
    page.add(
        ft.Column(
            [
                ft.Container(
                    content=ft.Row(
                        [tabs, ft.Row([theme_button, toggle_logs_button])],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.padding.only(left=20, right=20),
                    bgcolor=ft.colors.SURFACE_VARIANT,
                ),
                tabs_content,
                log_area,  # Добавляем область для логов
            ],
            expand=True,
        )
    )
    logger.info("Элементы добавлены на страницу")

    # Функция для обработки обратных вызовов от мониторов
    def process_callbacks():
        try:
            process_monitor.process_callbacks()
            performance_monitor.process_callbacks()
            page.update()
        except Exception as e:
            logger.exception(e, "Ошибка при обработке обратных вызовов:")

    # Флаг для управления работой таймера
    timer_running = True

    # Функция таймера с более коротким интервалом для более плавного обновления
    def timer_thread():
        logger.info("Запуск таймера обновления")
        while timer_running:
            try:
                # Вызываем обработку обратных вызовов
                process_callbacks()
                time.sleep(0.3)  # Уменьшаем интервал для более плавного обновления
            except Exception as e:
                logger.exception(e, "Ошибка в таймере:")
                time.sleep(1)  # Пауза при ошибке
        logger.info("Таймер обновления остановлен")

    # Запускаем таймер в отдельном потоке ПОСЛЕ добавления элементов на страницу
    timer_thread = threading.Thread(target=timer_thread, daemon=True)
    timer_thread.start()
    logger.debug("Таймер обновления запущен")

    # Функция для остановки таймера при закрытии приложения
    def on_close():
        logger.info("Закрытие приложения")
        nonlocal timer_running
        timer_running = False
        # Останавливаем мониторы
        process_monitor.stop_monitoring()
        performance_monitor.stop_monitoring()
        logger.info("Мониторы остановлены")

    # Регистрируем обработчик закрытия
    page.on_close = on_close
    logger.info("Обработчик закрытия зарегистрирован")
