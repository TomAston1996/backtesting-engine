from abc import ABC, abstractmethod


class IStrategy(ABC):
    @abstractmethod
    def generate_signals(self):
        pass
