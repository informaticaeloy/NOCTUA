# modules/base_module.py
from abc import ABC, abstractmethod

class ScanModule(ABC):
    def __init__(self, target):
        self.target = target
        self.status = 'pending'
        self.result = None

    @abstractmethod
    def run(self):
        pass

    def stop(self):
        # Implementar si el módulo puede detenerse
        pass
