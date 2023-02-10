from enum import Enum

class ProjectLogger:
    class prefix(Enum):
        WARNING = "WARNING"
        MAINTANENCE = "MAINTANENCE"
        ERROR = "ERROR"
        INFO = "INFO"
    
    @staticmethod
    def log(used_prefix: prefix, lines: list, status = None):
        for line in lines:
            print(f"[{used_prefix.value}] {line}")
            