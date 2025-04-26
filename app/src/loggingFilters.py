import logging


class RedactingFilter(logging.Filter):
    """
    A filter that redacts sensitive information from log messages.
    """

    def __init__(self, sensitiveFields: list[str]):
        super().__init__()
        self.sensitiveFields = sensitiveFields


    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter the log record to redact sensitive information.
        """
        for field in self.sensitiveFields:
            if record.args is None:
                continue
            if len(record.args) != 5:
                continue
            args = list(record.args)
            args[0] = "<<SECRET>>"
            msg = str(args[2])
            if field in msg:
                start = msg.index(field)
                lenght = len(field) + 1
                end = msg[start + lenght:].find("&")
                if end == -1:
                    end = len(msg)
                else:
                    end += start + lenght
                msg = msg[:start + lenght] + "<<SECRET>>" + msg[end:]
                args[2] = msg
            record.args = tuple(args)
        return True
