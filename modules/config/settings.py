# Настройки приложения
WINDOW_SETTINGS = {
    "title": "Системный монитор",
    "width": 1000,
    "height": 1000,
}

TABLE_SETTINGS = {
    "height": 700,
    "padding": 15,
}

# Настройки мониторинга
MONITORING_SETTINGS = {
    "process_update_interval": 2,  # секунды
    "performance_update_interval": 1,  # секунды
    "performance_history_length": 60,  # количество точек в истории
}

# Список тестовых процессов (используется только при отладке)
TEST_PROCESSES = [
    ["chrome.exe", "1234", "156.2", "2.5", "Running"],
    ["firefox.exe", "2345", "245.7", "3.8", "Running"],
    ["code.exe", "3456", "380.4", "4.2", "Running"],
    # ... добавьте остальные процессы из gui.py ...
]
