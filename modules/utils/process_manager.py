class ProcessManager:
    @staticmethod
    def filter_processes(processes, search_text):
        if not search_text:
            return processes.copy()
        search_text = search_text.lower()
        return [
            process
            for process in processes
            if search_text in process[0].lower()
            or search_text in process[1]
            or search_text in process[2]
            or search_text in process[3]
            or search_text in process[4].lower()
        ]

    @staticmethod
    def sort_processes(processes, column_index, ascending=True):
        def to_number(value):
            try:
                return float(
                    value.replace(" ГБ", "").replace(" МБ", "").replace("%", "")
                )
            except:
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
            key = lambda x: x[0].lower()

        return sorted(processes, key=key, reverse=not ascending)
