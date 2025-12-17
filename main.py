from src.core.app import GeminiApp
from src.ui.main_ui import MainUI

if __name__ == "__main__":
    app = GeminiApp()
    ui = MainUI(app)
    ui.run()
