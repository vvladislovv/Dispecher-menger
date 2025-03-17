from modules.utils.logger import get_logger

# Инициализация логгера
logger = get_logger()


class ProcessManager:
    @staticmethod
    def filter_processes(processes, search_text):
        """
        Фильтрует список процессов по поисковому запросу.

        Аргументы:
            processes (list): Список процессов для фильтрации
            search_text (str): Текст для поиска

        Возвращает:
            list: Отфильтрованный список процессов

        Действия:
            1. Если поисковый запрос пустой, возвращает исходный список
            2. Фильтрует процессы по имени и PID, содержащим поисковый запрос
            3. Возвращает отфильтрованный список
        """
        logger.debug(f"Фильтрация процессов по тексту: '{search_text}'")
        if not search_text:
            return processes.copy()
        search_text = search_text.lower()
        filtered_processes = [
            process
            for process in processes
            if search_text in process[0].lower()
            or search_text in process[1]
            or search_text in process[2]
            or search_text in process[3]
            or search_text in process[4].lower()
        ]
        logger.info(
            f"Отфильтровано {len(filtered_processes)} из {len(processes)} процессов"
        )
        return filtered_processes

    @staticmethod
    def sort_processes(processes, column_index, ascending=True):
        logger.debug(
            f"Сортировка процессов по колонке {column_index}, ascending={ascending}"
        )

        def to_number(value):
            try:
                return float(
                    value.replace(" ГБ", "").replace(" МБ", "").replace("%", "")
                )
            except Exception as e:
                logger.warning(
                    f"Ошибка преобразования значения '{value}' в число: {str(e)}"
                )
                return 0

        if column_index == 0:  # Имя процесса
            key = lambda x: x[0].lower()
        elif column_index == 1:  # PID
            key = lambda x: int(x[1])
        elif column_index == 2:  # Память (МБ)
            key = lambda x: to_number(x[2])
        elif column_index == 3:  # CPU %
            key = lambda x: to_number(x[3])
        else:
            logger.warning(
                f"Неизвестный индекс колонки: {column_index}, используется сортировка по имени"
            )
            key = lambda x: x[0].lower()

        sorted_processes = sorted(processes, key=key, reverse=not ascending)
        logger.debug(f"Процессы отсортированы успешно")
        return sorted_processes
