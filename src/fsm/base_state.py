from abc import ABC, abstractmethod

class BaseState(ABC):
    def __init__(self, app):
        self.app = app

    def enter(self):
        """Called when entering the state"""
        pass

    def exit(self):
        """Called when exiting the state"""
        pass

    @abstractmethod
    def run(self):
        """ run the state logic. """
        pass
