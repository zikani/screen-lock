import sys
import os
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QMessageBox
from PyQt5.QtCore import Qt, QAbstractNativeEventFilter, QEvent
from PyQt5.QtGui import QIcon
import win32con
from screenlocker import ScreenLocker
from settingspanel import SettingsPanel
from utils import is_windows, load_settings, request_admin_privileges, save_settings, set_as_default_lock_screen

# Add WinEventFilter class for hotkey handling
class WinEventFilter(QAbstractNativeEventFilter):
    def __init__(self, locker):
        super().__init__()
        self.locker = locker

    def nativeEventFilter(self, eventType, message):
        if is_windows() and eventType == "windows_generic_MSG":
            try:
                import ctypes
                from ctypes.wintypes import MSG
                msg = ctypes.cast(int(message), ctypes.POINTER(MSG)).contents
                if msg.message == win32con.WM_HOTKEY:
                    if msg.wParam == 1:  # Our hotkey ID
                        self.locker.lock_screen()
                        return True, 0
            except Exception as e:
                print(f"Error in native event filter: {e}")
        return False, 0

class ScreenLockerApp:
    def __init__(self):
        # Check if admin rights are needed and restart if necessary
        if self.needs_admin_privileges():
            if request_admin_privileges():
                # If we get here, we're in the elevated process
                QMessageBox.information(None, "Administrator Rights",
                                        "Running with administrator privileges.")
            else:
                # Original process exits after spawning elevated one
                sys.exit(0)

        # Load settings
        try:
            self.settings = load_settings()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to load settings: {e}")
            self.settings = load_settings(default=True)  # Fallback to default settings

        # Create the screen locker
        try:
            self.locker = ScreenLocker(self.settings)
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to initialize screen locker: {e}")
            sys.exit(1)  # Exit if the locker cannot be initialized

        # Create the settings panel
        self.settings_panel = SettingsPanel(self.settings, self.locker)

        # Create system tray icon
        self.setup_tray_icon()

        # Create and install the event filter
        if is_windows():
            self.win_event_filter = WinEventFilter(self.locker)
            app = QApplication.instance()
            app.installNativeEventFilter(self.win_event_filter)

    def needs_admin_privileges(self):
        """Check if the app needs admin privileges based on settings."""
        try:
            settings = load_settings()
            return (settings.get("set_as_default_lock", False) or
                    settings.get("secure_desktop", False))
        except:
            return False

    def setup_windows_integration(self):
        """Set up Windows-specific integrations."""
        if not is_windows():
            return

        try:
            if self.settings.get("set_as_default_lock", False):
                success, message = set_as_default_lock_screen(True)
                if not success:
                    QMessageBox.warning(None, "Windows Integration", message)

            # Register for Win+L if enabled
            if self.settings.get("replace_win_l", True):
                import win32con
                import win32gui
                try:
                    # Attempt to unregister previous hotkey by simply trying to register again.
                    # This is a less reliable but widely compatible approach.
                    try:
                        win32gui.UnregisterHotKey(None, 1) #try to unregister
                    except:
                        pass # if it fail, it doesn't matter, we will try to register anyway

                    # Register new hotkey (Win+L)
                    if not win32gui.RegisterHotKey(None, 1, win32con.MOD_WIN, ord('L')):
                        raise Exception("Failed to register Win+L hotkey")
                except Exception as e:
                    QMessageBox.warning(None, "Hotkey Registration",
                                        f"Failed to register Win+L hotkey: {str(e)}")
        except Exception as e:
            QMessageBox.warning(None, "Windows Integration",
                                f"Failed to set up Windows integration: {str(e)}")

    def init_app(self):
        # Set up integrations immediately after admin check
        try:
            self.setup_windows_integration()
            if self.settings.get("set_as_default_lock", False):
                success, message = set_as_default_lock_screen(True)
                if success:
                    # Launch the Windows lock screen settings to complete setup
                    if is_windows():
                        os.system("ms-settings:lockscreen")
        except Exception as e:
            QMessageBox.warning(None, "Integration Setup",
                                f"Failed to set up some integrations: {str(e)}")

        # Create system tray icon
        self.setup_tray_icon()

    def setup_tray_icon(self):
        """Set up the system tray icon and menu."""
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setToolTip("Screen Locker")

        # Set icon - use a custom icon if available, otherwise use a standard icon
        icon_path = os.path.join(os.path.dirname(__file__), "icons", "lock.png")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            self.tray_icon.setIcon(QApplication.style().standardIcon(QApplication.style().SP_ComputerIcon))

        # Create tray menu
        tray_menu = QMenu()

        # Add menu actions
        lock_action = QAction("Lock Screen", self.tray_icon)
        lock_action.triggered.connect(self.locker.lock_screen)

        settings_action = QAction("Settings", self.tray_icon)
        settings_action.triggered.connect(self.show_settings)

        exit_action = QAction("Exit", self.tray_icon)
        exit_action.triggered.connect(self.exit_app)

        # Add actions to menu
        tray_menu.addAction(lock_action)
        tray_menu.addAction(settings_action)
        tray_menu.addAction(exit_action)

        # Set the tray menu
        self.tray_icon.setContextMenu(tray_menu)

        # Show the tray icon
        self.tray_icon.show()

    def show_settings(self):
        """Show the settings panel."""
        self.settings_panel.show()

    def exit_app(self):
        """Exit the application."""
        try:
            save_settings(self.settings)  # Save settings before exiting
        except Exception as e:
            QMessageBox.warning(None, "Warning", f"Failed to save settings: {e}")

        self.tray_icon.hide()  # Hide the tray icon
        QApplication.quit()  # Quit the application

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Ensure the app doesn't quit when the last window is closed

    # Create and run the screen locker app
    try:
        screen_locker_app = ScreenLockerApp()
        screen_locker_app.init_app()

        # Show success message after setup
        if is_windows() and screen_locker_app.settings.get("set_as_default_lock", False):
            QMessageBox.information(None, "Setup Complete",
                                    "Screen Locker has been set as your default lock screen.\n"
                                    "You can test it by pressing Win+L or using the system tray icon.")
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to initialize application: {e}")
        sys.exit(1)

    sys.exit(app.exec_())