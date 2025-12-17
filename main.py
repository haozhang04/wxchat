from src.core.app import App
from src.ui.main_ui import MainUI

if __name__ == "__main__":
    app = App()
    ui = MainUI(app)
    ui.run()
