from src.gui.display_manager import DisplayManager
from src.settings_utils import save_settings, load_settings

if __name__ == '__main__':
    try:
        load_settings()
       
        display_manager = DisplayManager()
        display_manager.run()
    finally:
        save_settings()
