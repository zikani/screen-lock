import os
import sys
import time
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLineEdit, QApplication, QDesktopWidget)
from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal, QEvent
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap, QKeySequence, QBrush
from PyQt5.QtCore import QObject, QEvent
from utils import get_idle_time, parse_hotkey, fullscreen_on_all_monitors

# Explicitly export the ScreenLocker class
__all__ = ['ScreenLocker']

class LockScreen(QWidget):
    """Widget to display the locked screen."""   
    def __init__(self, settings, parent=None, screen_geometry=None):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        self.settings = settings
        self.password_attempt = ""
        self.parent_locker = parent  # Store the ScreenLocker instance
        
        # Set up the window
        if screen_geometry:
            self.setGeometry(screen_geometry)
        else:
            self.showFullScreen()
        
        self.setWindowTitle("Screen Locked")
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Set background
        self.setup_background()
        
        # Create layout
        self.setup_layout()
        
        # Install event filter for keyboard events
        self.installEventFilter(self)
        
    def setup_background(self):
        # Set up the background
        palette = self.palette()
        
        if self.settings.get("bg_image"):
            # Use background image
            try:
                pixmap = QPixmap(self.settings["bg_image"])
                if not pixmap.isNull():
                    palette.setBrush(QPalette.Window, QBrush(pixmap.scaled(
                        self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)))
                else:
                    # Fall back to black if image loading fails
                    palette.setColor(QPalette.Window, QColor("#000000"))
            except:
                # Fall back to black if any error occurs
                palette.setColor(QPalette.Window, QColor("#000000"))
        else:
            # Use solid color
            bg_color = self.settings.get("bg_color", "#000000")
            palette.setColor(QPalette.Window, QColor(bg_color))
            
        self.setPalette(palette)
        
    def setup_layout(self):
        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(50, 50, 50, 50)
        
        # Add spacer to push content to center
        main_layout.addStretch(1)
        
        # Add clock if enabled
        if self.settings.get("enable_clock", True):
            self.clock_label = QLabel()
            self.update_clock()
            
            # Add clock emoji if no custom icon
            if not self.settings.get("clock_icon"):
                self.clock_label.setText("🕐 " + self.clock_label.text())
            
            # Set font properties
            font_size = self.settings.get("clock_size", 10)
            font = QFont()
            font.setPointSize(font_size)
            self.clock_label.setFont(font)
            
            # Set color
            clock_color = self.settings.get("clock_color", "#FFFFFF")
            self.clock_label.setStyleSheet(f"color: {clock_color}")
            
            # Update clock every second
            self.clock_timer = QTimer(self)
            self.clock_timer.timeout.connect(self.update_clock)
            self.clock_timer.start(1000)
            
            main_layout.addWidget(self.clock_label, 0, Qt.AlignCenter)
        
        # Add user icon/avatar if enabled
        if self.settings.get("show_user_avatar", True):
            user_avatar = QLabel()
            avatar_size = QSize(96, 96)
            user_avatar.setFixedSize(avatar_size)
            
            # Try to load user avatar
            avatar_path = self.settings.get("user_avatar_path", "")
            if avatar_path and os.path.exists(avatar_path):
                pixmap = QPixmap(avatar_path)
            else:
                # Use default user icon emoji as fallback
                user_avatar.setText("👤")
                user_avatar.setFont(QFont("", 68))
                user_avatar.setAlignment(Qt.AlignCenter)
            
            if 'pixmap' in locals():
                pixmap = pixmap.scaled(avatar_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                user_avatar.setPixmap(pixmap)
            
            user_avatar.setStyleSheet("""
                QLabel {
                    background-color: rgba(255, 255, 255, 0.1);
                    border-radius: 48px;
                    padding: 8px;
                }
            """)
            main_layout.addWidget(user_avatar, 0, Qt.AlignCenter)
            
        # Add user name if enabled
        if self.settings.get("show_username", True):
            try:
                import getpass
                username = self.settings.get("custom_username", getpass.getuser())
                user_label = QLabel(username)
                user_label.setFont(QFont("", 14))
                user_label.setStyleSheet("color: white; margin: 10px;")
                main_layout.addWidget(user_label, 0, Qt.AlignCenter)
            except Exception as e:
                print(f"Error getting username: {e}")
        
        # Add some space
        main_layout.addSpacing(20)
        
        # Add locked message with lock emoji if no custom icon
        lock_icon = "🔒 " if not self.settings.get("lock_icon") else ""
        lock_label = QLabel(f"{lock_icon}Screen Locked")
        lock_font = QFont()
        lock_font.setPointSize(18)
        lock_label.setFont(lock_font)
        lock_label.setStyleSheet("color: white")
        main_layout.addWidget(lock_label, 0, Qt.AlignCenter)
        
        # Add spacing before the unlock interface
        main_layout.addSpacing(20)
        
        if self.settings.get("enable_password", False):
            # Add key emoji to password field if no custom icon
            password_icon = "🔑 " if not self.settings.get("password_icon") else ""
            self.password_field = QLineEdit()
            self.password_field.setEchoMode(QLineEdit.Password)
            self.password_field.setPlaceholderText(f"{password_icon}Enter password to unlock")
            self.password_field.setStyleSheet("""
                QLineEdit {
                    padding: 10px;
                    border-radius: 5px;
                    background-color: rgba(255, 255, 255, 0.2);
                    color: white;
                    border: 1px solid white;
                    font-size: 14px;
                    min-width: 300px;
                }
            """)
            self.password_field.returnPressed.connect(self.check_password)
            self.password_field.setFocus()  # Set initial focus to password field
            
            # Add password field to layout
            password_layout = QHBoxLayout()
            password_layout.addStretch(1)
            password_layout.addWidget(self.password_field)
            password_layout.addStretch(1)
            main_layout.addLayout(password_layout)
            
            # Add message label for password feedback
            self.message_label = QLabel("")
            self.message_label.setStyleSheet("color: red")
            main_layout.addWidget(self.message_label, 0, Qt.AlignCenter)

        # Add unlock icon to button if no custom icon
        unlock_icon = "🔓 " if not self.settings.get("unlock_icon") else ""
        unlock_button = QPushButton(f"{unlock_icon}{'Sign in' if self.settings.get('enable_password', False) else 'Unlock'}")
        unlock_button.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                border-radius: 5px;
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid white;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.4);
            }
        """)
        unlock_button.clicked.connect(self.check_password if self.settings.get("enable_password", False) else self.unlock_screen)
        
        # Add unlock button to layout
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(unlock_button)
        button_layout.addStretch(1)
        main_layout.addLayout(button_layout)
        
        # Add spacer to push content to center
        main_layout.addStretch(1)
        
        self.setLayout(main_layout)
        
    def update_clock(self):
        # Update the clock label with current time
        if hasattr(self, "clock_label"):
            current_time = datetime.now()
            
            # Format based on settings
            if self.settings.get("clock_24h", False):
                time_format = "%H:%M:%S"
            else:
                time_format = "%I:%M:%S %p"
                
            time_text = current_time.strftime(time_format)
            self.clock_label.setText(time_text)
    
    def check_password(self):
        """Check if the entered password is correct."""
        if not hasattr(self, "password_field"):
            self.unlock_screen()
            return

        entered_password = self.password_field.text()
        stored_password = self.settings.get("password", "")

        # Import verify_password from utils
        from utils import verify_password
        
        # Check if the password is correct
        if (stored_password and verify_password(entered_password, stored_password)) or not stored_password:
            self.unlock_screen()
        else:
            self.message_label.setText("Incorrect password")
            self.password_field.clear()
            self.password_field.setFocus()  # Keep focus on password field after failed attempt
    
    def unlock_screen(self):
        # Unlock the screen
        if self.parent_locker:
            self.parent_locker.unlock_screen()
        else:
            self.close()
    
    def eventFilter(self, obj, event):
        """Handle keyboard and mouse events."""
        if event.type() == QEvent.KeyPress:
            # Debug mode: Force close with Escape key only in debug mode
            if event.key() == Qt.Key_Escape and self.settings.get("debug_mode", False):
                print("Debug: Force closing lock screen")
                self.unlock_screen()
                return True

            # Always allow keyboard input for password field
            if hasattr(self, "password_field"):
                self.password_field.setFocus()
                return False  # Let the password field handle the event

        elif event.type() == QEvent.MouseButtonPress:
            # Set focus to password field on mouse click
            if hasattr(self, "password_field"):
                self.password_field.setFocus()
                return True

        return super().eventFilter(obj, event)
    
    def resizeEvent(self, event):
        # Update background when window is resized
        self.setup_background()
        super().resizeEvent(event)

    def showEvent(self, event):
        """Handle window show event."""
        super().showEvent(event)
        # Set focus to password field when window is shown
        if hasattr(self, "password_field"):
            self.password_field.setFocus()

class ScreenLocker(QObject):
    """Main class to manage the screen locking functionality."""
    def __init__(self, settings):
        super().__init__()
        
        self.settings = settings
        self.lock_screens = []
        self.is_locked = False
        
        # Set up the idle timer if enabled
        self.setup_idle_timer()
    
    def setup_idle_timer(self):
        # Set up the idle timer for automatic locking
        if self.settings.get("enable_timer", False):
            # Create and start the idle check timer
            self.idle_timer = QTimer()
            self.idle_timer.timeout.connect(self.check_idle_time)
            self.idle_timer.start(10000)  # Check every 10 seconds
    
    def check_idle_time(self):
        # Check if the system has been idle for the timeout period
        if not self.is_locked:
            idle_time = get_idle_time()
            idle_timeout = self.settings.get("idle_timeout", 5) * 60  # Convert minutes to seconds
            
            if idle_time >= idle_timeout:
                self.lock_screen()
    
    def unlock_screen(self):
        """Unlock the screen."""
        if self.is_locked:
            self.is_locked = False
            
            # Close all lock screens
            for screen in self.lock_screens:
                screen.close()
            
            # Clear the list of lock screens
            self.lock_screens.clear()  # Use clear() instead of reassignment
    
    def lock_screen(self):
        # Lock the screen
        if not self.is_locked:
            self.is_locked = True
            
            # Create a lock screen for each monitor
            geometries = fullscreen_on_all_monitors()
            
            for geometry in geometries:
                lock_screen = LockScreen(self.settings, self, geometry)  # Pass self as parent
                lock_screen.show()
                self.lock_screens.append(lock_screen)
    
    def apply_settings(self, new_settings):
        # Apply new settings
        self.settings = new_settings
        
        # Update idle timer
        if hasattr(self, "idle_timer"):
            self.idle_timer.stop()
            
        self.setup_idle_timer()
        
        # Update lock screens if currently locked
        if self.is_locked:
            self.unlock_screen()
            self.lock_screen()