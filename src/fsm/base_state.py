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

    def change(self):
        """
        Called to handle state transition logic.
        Returns:
             AppState or None: The next state to transition to, or None to stay in current state.
        """
        return None

    @abstractmethod
    def run(self):
        """
        run the state logic. 
        Returns:
            bool: True to continue the application loop, False to exit.
        """
        pass
