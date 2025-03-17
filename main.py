import flet as ft
from modules.ui.app import SystemMonitorApp
from modules.utils.logger import get_logger

# Инициализация логгера
logger = get_logger()


def main():
    logger.info("Запуск приложения Системный монитор")
    try:
        # Настройка отображения логов в чате приложения
        def show_log_in_chat(message):
            # Эта функция будет переопределена в SystemMonitorApp
            # для отображения логов в интерфейсе
            print(message)

        logger.set_chat_callback(show_log_in_chat)

        # Запуск приложения
        ft.app(SystemMonitorApp)
        logger.info("Приложение завершило работу")
    except Exception as e:
        logger.exception(e, "Критическая ошибка при запуске приложения:")


if __name__ == "__main__":
    main()
