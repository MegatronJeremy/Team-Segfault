from src.gui.display_manager import DisplayManager
from src.settings_utils import load_settings

if __name__ == '__main__':
    load_settings()

    display_manager = DisplayManager()
    display_manager.run()
