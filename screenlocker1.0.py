from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QCursor
import json
import os
import sys
import hashlib
import random
import string

class SettingsPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lock Screen Settings")
        self.setMinimumSize(500, 700)
        self.settings = self.load_settings()

        # Initialize inactivity timer
        self.inactivity_timer = QTimer()
        self.inactivity_timer.timeout.connect(self.lock_screen)
        self.reset_inactivity_timer()

        # Track mouse movements to detect inactivity
        self.setMouseTracking(True)
        self.installEventFilter(self)

        # Initialize LockScreen instance
        self.screen_lock = None

        # Create layout
        layout = QtWidgets.QVBoxLayout()

        # Create a tab widget for better organization
        self.tab_widget = QtWidgets.QTabWidget()

        # --- General Tab ---
        general_tab = QtWidgets.QWidget()
        general_layout = QtWidgets.QVBoxLayout()

        # Theme selection
        theme_layout = QtWidgets.QHBoxLayout()
        theme_label = QtWidgets.QLabel("Theme:")
        self.theme_combo = QtWidgets.QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Custom"])
        self.theme_combo.setCurrentText(self.settings.get('theme', 'Dark'))
        self.theme_combo.currentTextChanged.connect(self.apply_theme)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        general_layout.addLayout(theme_layout)

        # Timeout settings
        timeout_layout = QtWidgets.QHBoxLayout()
        timeout_label = QtWidgets.QLabel("Lock screen timeout (minutes):")
        self.timeout_spinbox = QtWidgets.QSpinBox()
        self.timeout_spinbox.setValue(self.settings.get('timeout', 5))
        self.timeout_spinbox.setRange(1, 60)
        self.timeout_spinbox.setToolTip("Set the time (in minutes) after which the screen locks automatically.")
        timeout_layout.addWidget(timeout_label)
        timeout_layout.addWidget(self.timeout_spinbox)
        general_layout.addLayout(timeout_layout)

        # Hot corners toggle
        self.hot_corners_checkbox = QtWidgets.QCheckBox("Enable hot corners to prevent lock")
        self.hot_corners_checkbox.setChecked(self.settings.get('hot_corners', False))
        self.hot_corners_checkbox.setToolTip("Move the cursor to a corner to prevent the screen from locking.")
        general_layout.addWidget(self.hot_corners_checkbox)

        # Lock on startup option
        self.lock_on_startup_checkbox = QtWidgets.QCheckBox("Lock screen on system startup")
        self.lock_on_startup_checkbox.setChecked(self.settings.get('lock_on_startup', False))
        self.lock_on_startup_checkbox.setToolTip("Automatically lock screen when system starts.")
        general_layout.addWidget(self.lock_on_startup_checkbox)

        # Lock on sleep/hibernate option
        self.lock_on_sleep_checkbox = QtWidgets.QCheckBox("Lock screen on sleep/hibernate")
        self.lock_on_sleep_checkbox.setChecked(self.settings.get('lock_on_sleep', True))
        self.lock_on_sleep_checkbox.setToolTip("Automatically lock screen when system goes to sleep or hibernates.")
        general_layout.addWidget(self.lock_on_sleep_checkbox)

        general_tab.setLayout(general_layout)

        # --- Security Tab ---
        security_tab = QtWidgets.QWidget()
        security_layout = QtWidgets.QVBoxLayout()

        # Password configuration
        password_group = QtWidgets.QGroupBox("Password Configuration")
        password_layout = QtWidgets.QFormLayout()

        self.password_field = QtWidgets.QLineEdit()
        self.password_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_field.setText(self.settings.get('password', ''))
        password_layout.addRow("New Password:", self.password_field)

        self.confirm_password_field = QtWidgets.QLineEdit()
        self.confirm_password_field.setEchoMode(QtWidgets.QLineEdit.Password)
        password_layout.addRow("Confirm Password:", self.confirm_password_field)

        # Password strength indicator
        self.password_strength_label = QtWidgets.QLabel("Password Strength: ")
        self.password_strength_indicator = QtWidgets.QProgressBar()
        self.password_strength_indicator.setRange(0, 100)
        self.password_strength_indicator.setValue(0)
        self.password_field.textChanged.connect(self.update_password_strength)
        password_layout.addRow(self.password_strength_label, self.password_strength_indicator)

        # Password generation
        generate_password_button = QtWidgets.QPushButton("Generate Strong Password")
        generate_password_button.clicked.connect(self.generate_strong_password)
        password_layout.addRow(generate_password_button)

        # Security options
        self.hash_passwords_checkbox = QtWidgets.QCheckBox("Use secure password hashing")
        self.hash_passwords_checkbox.setChecked(self.settings.get('hash_passwords', True))
        self.hash_passwords_checkbox.setToolTip("Store passwords securely using SHA-256 hash.")
        password_layout.addRow(self.hash_passwords_checkbox)

        # Two factor authentication option
        self.two_factor_checkbox = QtWidgets.QCheckBox("Enable two-factor authentication")
        self.two_factor_checkbox.setChecked(self.settings.get('two_factor', False))
        self.two_factor_checkbox.setToolTip("Require additional verification method.")
        password_layout.addRow(self.two_factor_checkbox)

        # Failed attempt settings
        max_attempts_layout = QtWidgets.QHBoxLayout()
        max_attempts_label = QtWidgets.QLabel("Max failed login attempts:")
        self.max_attempts_spinbox = QtWidgets.QSpinBox()
        self.max_attempts_spinbox.setValue(self.settings.get('max_attempts', 3))
        self.max_attempts_spinbox.setRange(1, 10)
        max_attempts_layout.addWidget(max_attempts_label)
        max_attempts_layout.addWidget(self.max_attempts_spinbox)
        password_layout.addRow(max_attempts_layout)

        # Lockout duration
        lockout_layout = QtWidgets.QHBoxLayout()
        lockout_label = QtWidgets.QLabel("Lockout duration (minutes):")
        self.lockout_spinbox = QtWidgets.QSpinBox()
        self.lockout_spinbox.setValue(self.settings.get('lockout_duration', 5))
        self.lockout_spinbox.setRange(1, 60)
        lockout_layout.addWidget(lockout_label)
        lockout_layout.addWidget(self.lockout_spinbox)
        password_layout.addRow(lockout_layout)

        # Recovery email option
        recovery_layout = QtWidgets.QHBoxLayout()
        recovery_label = QtWidgets.QLabel("Recovery Email:")
        self.recovery_email = QtWidgets.QLineEdit()
        self.recovery_email.setText(self.settings.get('recovery_email', ''))
        self.recovery_email.setPlaceholderText("Enter recovery email address")
        recovery_layout.addWidget(recovery_label)
        recovery_layout.addWidget(self.recovery_email)
        password_layout.addRow(recovery_layout)

        password_group.setLayout(password_layout)
        security_layout.addWidget(password_group)

        security_tab.setLayout(security_layout)

        # --- Appearance Tab ---
        appearance_tab = QtWidgets.QWidget()
        appearance_layout = QtWidgets.QVBoxLayout()

        # Custom wallpaper
        wallpaper_group = QtWidgets.QGroupBox("Wallpaper")
        wallpaper_layout = QtWidgets.QVBoxLayout()

        self.wallpaper_label = QtWidgets.QLabel()
        self.wallpaper_label.setAlignment(QtCore.Qt.AlignCenter)
        self.wallpaper_label.setFixedSize(200, 150)
        self.wallpaper_label.setStyleSheet("border: 2px dashed #ccc;")
        self.update_wallpaper_preview(self.settings.get('wallpaper', ''))
        wallpaper_layout.addWidget(self.wallpaper_label)

        wallpaper_buttons_layout = QtWidgets.QHBoxLayout()
        browse_button = QtWidgets.QPushButton("Browse...")
        browse_button.clicked.connect(self.choose_wallpaper)
        wallpaper_buttons_layout.addWidget(browse_button)

        # New wallpaper options
        random_wallpaper_button = QtWidgets.QPushButton("Use Random Wallpaper")
        random_wallpaper_button.clicked.connect(self.use_random_wallpaper)
        wallpaper_buttons_layout.addWidget(random_wallpaper_button)

        clear_wallpaper_button = QtWidgets.QPushButton("Clear Wallpaper")
        clear_wallpaper_button.clicked.connect(self.clear_wallpaper)
        wallpaper_buttons_layout.addWidget(clear_wallpaper_button)

        wallpaper_layout.addLayout(wallpaper_buttons_layout)

        # Wallpaper slide show option
        self.slideshow_checkbox = QtWidgets.QCheckBox("Enable wallpaper slideshow")
        self.slideshow_checkbox.setChecked(self.settings.get('slideshow_enabled', False))
        wallpaper_layout.addWidget(self.slideshow_checkbox)

        slideshow_interval_layout = QtWidgets.QHBoxLayout()
        slideshow_interval_label = QtWidgets.QLabel("Change interval (minutes):")
        self.slideshow_interval_spinbox = QtWidgets.QSpinBox()
        self.slideshow_interval_spinbox.setValue(self.settings.get('slideshow_interval', 5))
        self.slideshow_interval_spinbox.setRange(1, 60)
        slideshow_interval_layout.addWidget(slideshow_interval_label)
        slideshow_interval_layout.addWidget(self.slideshow_interval_spinbox)
        wallpaper_layout.addLayout(slideshow_interval_layout)

        self.slideshow_folder = QtWidgets.QLineEdit()
        self.slideshow_folder.setText(self.settings.get('slideshow_folder', ''))
        self.slideshow_folder.setReadOnly(True)
        slideshow_folder_layout = QtWidgets.QHBoxLayout()
        slideshow_folder_layout.addWidget(QtWidgets.QLabel("Slideshow Folder:"))
        slideshow_folder_layout.addWidget(self.slideshow_folder)
        browse_folder_button = QtWidgets.QPushButton("Browse...")
        browse_folder_button.clicked.connect(self.choose_slideshow_folder)
        slideshow_folder_layout.addWidget(browse_folder_button)
        wallpaper_layout.addLayout(slideshow_folder_layout)

        wallpaper_group.setLayout(wallpaper_layout)
        appearance_layout.addWidget(wallpaper_group)

        # Display options group
        display_group = QtWidgets.QGroupBox("Display Options")
        display_layout = QtWidgets.QVBoxLayout()

        # Clock display toggle
        self.clock_checkbox = QtWidgets.QCheckBox("Show clock on lock screen")
        self.clock_checkbox.setChecked(self.settings.get('show_clock', True))
        self.clock_checkbox.setToolTip("Display a clock on the lock screen.")
        display_layout.addWidget(self.clock_checkbox)

        # Clock format option
        clock_format_layout = QtWidgets.QHBoxLayout()
        clock_format_label = QtWidgets.QLabel("Clock Format:")
        self.clock_format_combo = QtWidgets.QComboBox()
        self.clock_format_combo.addItems(["12-hour", "24-hour"])
        self.clock_format_combo.setCurrentText(self.settings.get('clock_format', '24-hour'))
        clock_format_layout.addWidget(clock_format_label)
        clock_format_layout.addWidget(self.clock_format_combo)
        display_layout.addLayout(clock_format_layout)

        # Show date option
        self.show_date_checkbox = QtWidgets.QCheckBox("Show date on lock screen")
        self.show_date_checkbox.setChecked(self.settings.get('show_date', True))
        display_layout.addWidget(self.show_date_checkbox)

        # Date format option
        date_format_layout = QtWidgets.QHBoxLayout()
        date_format_label = QtWidgets.QLabel("Date Format:")
        self.date_format_combo = QtWidgets.QComboBox()
        self.date_format_combo.addItems(["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD"])
        self.date_format_combo.setCurrentText(self.settings.get('date_format', 'MM/DD/YYYY'))
        date_format_layout.addWidget(date_format_label)
        date_format_layout.addWidget(self.date_format_combo)
        display_layout.addLayout(date_format_layout)

        # Background blur option
        self.blur_checkbox = QtWidgets.QCheckBox("Apply background blur effect")
        self.blur_checkbox.setChecked(self.settings.get('background_blur', False))
        display_layout.addWidget(self.blur_checkbox)

        # Blur intensity
        blur_intensity_layout = QtWidgets.QHBoxLayout()
        blur_intensity_label = QtWidgets.QLabel("Blur Intensity:")
        self.blur_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.blur_slider.setRange(1, 20)
        self.blur_slider.setValue(self.settings.get('blur_intensity', 5))
        blur_intensity_layout.addWidget(blur_intensity_label)
        blur_intensity_layout.addWidget(self.blur_slider)
        display_layout.addLayout(blur_intensity_layout)

        # Background color picker
        color_layout = QtWidgets.QHBoxLayout()
        color_label = QtWidgets.QLabel("Background color:")
        self.color_button = QtWidgets.QPushButton()
        self.color_button.setFixedSize(30, 30)
        self.current_color = self.settings.get('background_color', '#000000')
        self.color_button.setStyleSheet(f"background-color: {self.current_color};")
        self.color_button.clicked.connect(self.choose_color)
        self.color_button.setToolTip("Choose a background color for the lock screen.")
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_button)
        color_layout.addStretch()
        display_layout.addLayout(color_layout)

        # Opacity slider
        opacity_layout = QtWidgets.QHBoxLayout()
        opacity_label = QtWidgets.QLabel("Background Opacity:")
        self.opacity_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(self.settings.get('background_opacity', 80))
        self.opacity_slider.setToolTip("Set the background opacity (0 = transparent, 100 = opaque)")
        opacity_layout.addWidget(opacity_label)
        opacity_layout.addWidget(self.opacity_slider)
        display_layout.addLayout(opacity_layout)

        display_group.setLayout(display_layout)
        appearance_layout.addWidget(display_group)

        appearance_tab.setLayout(appearance_layout)

        # Add tabs to the tab widget
        self.tab_widget.addTab(general_tab, "General")
        self.tab_widget.addTab(security_tab, "Security")
        self.tab_widget.addTab(appearance_tab, "Appearance")

        layout.addWidget(self.tab_widget)

        # Add save and cancel buttons
        buttons_layout = QtWidgets.QHBoxLayout()
        self.save_button = QtWidgets.QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)
        self.apply_theme()

    def load_settings(self):
        """Load settings from JSON file."""
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading settings: {e}")
            return {}

    def save_settings(self):
        """Save settings to JSON file."""
        try:
            # Validate password
            if self.password_field.text():
                if self.password_field.text() != self.confirm_password_field.text():
                    QMessageBox.warning(self, "Password Mismatch", "Passwords do not match.")
                    return

                # Hash password if option is selected
                if self.hash_passwords_checkbox.isChecked():
                    password_hash = hashlib.sha256(self.password_field.text().encode()).hexdigest()
                    self.settings['password'] = password_hash
                else:
                    self.settings['password'] = self.password_field.text()

            # Save other settings
            self.settings['theme'] = self.theme_combo.currentText()
            self.settings['timeout'] = self.timeout_spinbox.value()
            self.settings['hot_corners'] = self.hot_corners_checkbox.isChecked()
            self.settings['lock_on_startup'] = self.lock_on_startup_checkbox.isChecked()
            self.settings['lock_on_sleep'] = self.lock_on_sleep_checkbox.isChecked()
            self.settings['hash_passwords'] = self.hash_passwords_checkbox.isChecked()
            self.settings['two_factor'] = self.two_factor_checkbox.isChecked()
            self.settings['max_attempts'] = self.max_attempts_spinbox.value()
            self.settings['lockout_duration'] = self.lockout_spinbox.value()
            self.settings['recovery_email'] = self.recovery_email.text()
            self.settings['show_clock'] = self.clock_checkbox.isChecked()
            self.settings['clock_format'] = self.clock_format_combo.currentText()
            self.settings['show_date'] = self.show_date_checkbox.isChecked()
            self.settings['date_format'] = self.date_format_combo.currentText()
            self.settings['background_blur'] = self.blur_checkbox.isChecked()
            self.settings['blur_intensity'] = self.blur_slider.value()
            self.settings['background_color'] = self.current_color
            self.settings['background_opacity'] = self.opacity_slider.value()
            self.settings['slideshow_enabled'] = self.slideshow_checkbox.isChecked()
            self.settings['slideshow_interval'] = self.slideshow_interval_spinbox.value()
            self.settings['slideshow_folder'] = self.slideshow_folder.text()

            # Save to file
            with open("settings.json", "w") as f:
                json.dump(self.settings, f, indent=4)

            QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully.")
            self.close()

            # Activate screen lock after saving settings
            self.lock_screen()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving settings: {e}")

    def lock_screen(self):
        """Activate the screen lock."""
        try:
            # Close existing lock screen instance if it exists
            if self.screen_lock is not None:
                self.screen_lock.close()

            # Create a new LockScreen instance
            self.screen_lock = LockScreen(self.settings)

            # Connect the unlocked signal to a slot
            self.screen_lock.unlocked.connect(self.on_unlock)

            # Show the lock screen
            self.screen_lock.show()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to activate screen lock: {e}")

    def on_unlock(self):
        """Handle the unlocked signal from the lock screen."""
        QMessageBox.information(self, "Unlocked", "Screen unlocked successfully.")
        self.show()  # Restore the main window

    def reset_inactivity_timer(self):
        """Reset the inactivity timer."""
        timeout_minutes = self.settings.get('timeout', 5)
        self.inactivity_timer.start(timeout_minutes * 60 * 1000)  # Convert minutes to milliseconds

    def eventFilter(self, obj, event):
        """Detect user activity to reset the inactivity timer."""
        if event.type() in (QtCore.QEvent.MouseMove, QtCore.QEvent.KeyPress):
            self.reset_inactivity_timer()
        return super().eventFilter(obj, event)

    def update_password_strength(self):
        """Update password strength indicator."""
        password = self.password_field.text()
        strength = 0

        if len(password) >= 8:
            strength += 25
        if any(c.isdigit() for c in password):
            strength += 25
        if any(c.isupper() for c in password):
            strength += 25
        if any(c.islower() for c in password) and any(not c.isalnum() for c in password):
            strength += 25

        self.password_strength_indicator.setValue(strength)

        if strength <= 25:
            self.password_strength_indicator.setStyleSheet("QProgressBar::chunk { background-color: red; }")
            self.password_strength_label.setText("Password Strength: Weak")
        elif strength <= 50:
            self.password_strength_indicator.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
            self.password_strength_label.setText("Password Strength: Medium")
        elif strength <= 75:
            self.password_strength_indicator.setStyleSheet("QProgressBar::chunk { background-color: yellow; }")
            self.password_strength_label.setText("Password Strength: Good")
        else:
            self.password_strength_indicator.setStyleSheet("QProgressBar::chunk { background-color: green; }")
            self.password_strength_label.setText("Password Strength: Strong")

    def generate_strong_password(self):
        """Generate a strong password."""
        length = 12
        chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(chars) for _ in range(length))
        self.password_field.setText(password)
        self.confirm_password_field.setText(password)
        self.update_password_strength()

    def choose_wallpaper(self):
        """Open file dialog to choose wallpaper."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Wallpaper", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.settings['wallpaper'] = file_path
            self.update_wallpaper_preview(file_path)

    def update_wallpaper_preview(self, path):
        """Update the wallpaper preview."""
        if path and os.path.exists(path):
            pixmap = QtGui.QPixmap(path)
            scaled_pixmap = pixmap.scaled(
                self.wallpaper_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
            )
            self.wallpaper_label.setPixmap(scaled_pixmap)
            self.wallpaper_label.setStyleSheet("")
        else:
            self.wallpaper_label.setPixmap(QtGui.QPixmap())
            self.wallpaper_label.setStyleSheet("border: 2px dashed #ccc;")

    def use_random_wallpaper(self):
        """Use a random wallpaper from the system."""
        # For demonstration, we're just using a placeholder
        self.settings['wallpaper'] = "random"
        self.wallpaper_label.setPixmap(QtGui.QPixmap())
        self.wallpaper_label.setStyleSheet("background-color: #3498db; border: none;")
        QMessageBox.information(self, "Random Wallpaper", "Random wallpaper will be used on each lock.")

    def clear_wallpaper(self):
        """Clear the wallpaper selection."""
        self.settings['wallpaper'] = ""
        self.wallpaper_label.setPixmap(QtGui.QPixmap())
        self.wallpaper_label.setStyleSheet("border: 2px dashed #ccc;")

    def choose_slideshow_folder(self):
        """Open dialog to choose slideshow folder."""
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Slideshow Folder")
        if folder:
            self.slideshow_folder.setText(folder)

    def choose_color(self):
        """Open color picker dialog."""
        color = QtWidgets.QColorDialog.getColor(QtGui.QColor(self.current_color), self)
        if color.isValid():
            self.current_color = color.name()
            self.color_button.setStyleSheet(f"background-color: {self.current_color};")

    def apply_theme(self):
        """Apply the selected theme to the UI."""
        theme = self.theme_combo.currentText()
        if theme == "Light":
            self.setStyleSheet("""
                QWidget { background-color: #f0f0f0; color: #333333; }
                QTabWidget::pane { border: 1px solid #cccccc; }
                QTabBar::tab { background-color: #e0e0e0; color: #333333; padding: 8px 20px; border: 1px solid #cccccc; }
                QTabBar::tab:selected { background-color: #ffffff; }
                QPushButton { background-color: #e0e0e0; color: #333333; border: 1px solid #cccccc; padding: 5px 10px; }
                QPushButton:hover { background-color: #d0d0d0; }
                QLineEdit, QSpinBox, QComboBox { background-color: #ffffff; border: 1px solid #cccccc; padding: 5px; }
                QCheckBox, QLabel { color: #333333; }
                QGroupBox { border: 1px solid #cccccc; margin-top: 10px; }
                QGroupBox::title { color: #333333; }
            """)
        elif theme == "Dark":
            self.setStyleSheet("""
                QWidget { background-color: #2d2d2d; color: #f0f0f0; }
                QTabWidget::pane { border: 1px solid #555555; }
                QTabBar::tab { background-color: #3d3d3d; color: #f0f0f0; padding: 8px 20px; border: 1px solid #555555; }
                QTabBar::tab:selected { background-color: #2d2d2d; }
                QPushButton { background-color: #3d3d3d; color: #f0f0f0; border: 1px solid #555555; padding: 5px 10px; }
                QPushButton:hover { background-color: #4d4d4d; }
                QLineEdit, QSpinBox, QComboBox { background-color: #3d3d3d; border: 1px solid #555555; color: #f0f0f0; padding: 5px; }
                QCheckBox, QLabel { color: #f0f0f0; }
                QGroupBox { border: 1px solid #555555; margin-top: 10px; }
                QGroupBox::title { color: #f0f0f0; }
            """)
        else:  # Custom theme
            pass  # User can define their own theme in the future

class LockScreen(QtWidgets.QWidget):
    unlocked = QtCore.pyqtSignal()  # Signal to emit when successfully unlocked

    def __init__(self, settings=None):
        super().__init__()
        self.setWindowTitle("Lock Screen")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.showFullScreen()

        self.settings = settings if settings else self.load_settings()
        self.failed_attempts = 0
        self.locked_out = False
        self.lockout_timer = None

        # Set up UI
        self.init_ui()

        # Start inactivity timer
        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.timeout.connect(self.check_inactivity)
        self.inactivity_timer.start(10000)  # Check every 10 seconds

        # Set up slideshow timer if enabled
        if self.settings.get('slideshow_enabled', False):
            self.slideshow_timer = QTimer(self)
            self.slideshow_timer.timeout.connect(self.change_wallpaper)
            interval = self.settings.get('slideshow_interval', 5) * 60000  # Convert to milliseconds
            self.slideshow_timer.start(interval)
            self.wallpaper_files = []
            self.load_slideshow_images()

        # Track mouse movement for hot corners
        if self.settings.get('hot_corners', False):
            self.setMouseTracking(True)

        # Set up the last activity time
        self.last_activity_time = QtCore.QDateTime.currentDateTime()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Main container widget
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setAlignment(QtCore.Qt.AlignCenter)

        # Set background
        self.set_background()

        # Clock and date
        if self.settings.get('show_clock', True):
            self.clock_label = QLabel()
            self.clock_label.setAlignment(QtCore.Qt.AlignCenter)
            self.clock_label.setFont(QFont("Arial", 72, QFont.Bold))
            self.clock_label.setStyleSheet("color: white; background-color: transparent;")
            self.main_layout.addWidget(self.clock_label)

            # Update clock every second
            self.clock_timer = QTimer(self)
            self.clock_timer.timeout.connect(self.update_clock)
            self.clock_timer.start(1000)
            self.update_clock()

        if self.settings.get('show_date', True):
            self.date_label = QLabel()
            self.date_label.setAlignment(QtCore.Qt.AlignCenter)
            self.date_label.setFont(QFont("Arial", 24))
            self.date_label.setStyleSheet("color: white; background-color: transparent;")
            self.main_layout.addWidget(self.date_label)
            self.update_date()

        # Spacer
        self.main_layout.addSpacing(50)

        # Login form
        login_container = QWidget()
        login_container.setStyleSheet("background-color: rgba(0, 0, 0, 0.5); border-radius: 10px;")
        login_layout = QVBoxLayout(login_container)
        login_layout.setContentsMargins(30, 30, 30, 30)

        # Login prompt
        login_prompt = QLabel("Enter your password to unlock")
        login_prompt.setAlignment(QtCore.Qt.AlignCenter)
        login_prompt.setFont(QFont("Arial", 14))
        login_prompt.setStyleSheet("color: white; background-color: transparent;")
        login_layout.addWidget(login_prompt)

        # Password field
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.Password)
        self.password_field.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #555;
                border-radius: 5px;
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                font-size: 16px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        self.password_field.returnPressed.connect(self.attempt_unlock)
        login_layout.addWidget(self.password_field)

        # Unlock button
        self.unlock_button = QPushButton("Unlock")
        self.unlock_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        self.unlock_button.clicked.connect(self.attempt_unlock)
        login_layout.addWidget(self.unlock_button)

        # Error message
        self.error_label = QLabel()
        self.error_label.setAlignment(QtCore.Qt.AlignCenter)
        self.error_label.setStyleSheet("color: #e74c3c; background-color: transparent;")
        self.error_label.hide()
        login_layout.addWidget(self.error_label)

        # Add login container to main layout
        self.main_layout.addWidget(login_container)
        self.main_layout.addStretch()

        # Add main widget to the layout
        layout.addWidget(self.main_widget)
        self.setLayout(layout)

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == QtCore.Qt.Key_Escape:
            # Debug function: Force unlock on Esc key press
            print("Debug: Force unlocking the screen.")
            self.unlocked.emit()  # Emit the unlocked signal
            self.hide()  # Hide the lock screen
        else:
            super().keyPressEvent(event)

    def set_background(self):
        """Set the background of the lock screen."""
        wallpaper = self.settings.get('wallpaper', '')
        blur = self.settings.get('background_blur', False)
        opacity = self.settings.get('background_opacity', 80) / 100.0

        # Set background style
        if wallpaper and os.path.exists(wallpaper):
            # Set wallpaper as background
            pixmap = QtGui.QPixmap(wallpaper)

            if blur:
                # Apply blur effect
                blur_intensity = self.settings.get('blur_intensity', 5)
                image = pixmap.toImage()
                blur_effect = QtGui.QGraphicsBlurEffect()
                blur_effect.setBlurRadius(blur_intensity)

                # Apply blur effect to the image
                scene = QtWidgets.QGraphicsScene()
                pixmap_item = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap.fromImage(image))
                pixmap_item.setGraphicsEffect(blur_effect)
                scene.addItem(pixmap_item)

                # Render the blurred image
                blurred_image = QtGui.QImage(image.size(), QtGui.QImage.Format_ARGB32)
                blurred_image.fill(QtCore.Qt.transparent)
                painter = QtGui.QPainter(blurred_image)
                scene.render(painter)
                painter.end()

                pixmap = QtGui.QPixmap.fromImage(blurred_image)

            # Set the wallpaper as the background
            palette = self.palette()
            palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(pixmap))
            self.setPalette(palette)
            self.setAutoFillBackground(True)
        else:
            # Use solid color background
            bg_color = self.settings.get('background_color', '#000000')
            self.setStyleSheet(f"background-color: {bg_color};")

    def update_clock(self):
        """Update the clock display."""
        current_time = QtCore.QTime.currentTime()

        if self.settings.get('clock_format', '24-hour') == '12-hour':
            time_format = "hh:mm:ss AP"
        else:
            time_format = "HH:mm:ss"

        time_text = current_time.toString(time_format)
        self.clock_label.setText(time_text)

    def update_date(self):
        """Update the date display."""
        current_date = QtCore.QDate.currentDate()
        date_format = self.settings.get('date_format', 'MM/DD/YYYY')

        format_map = {
            'MM/DD/YYYY': 'MM/dd/yyyy',
            'DD/MM/YYYY': 'dd/MM/yyyy',
            'YYYY-MM-DD': 'yyyy-MM-dd'
        }

        qt_format = format_map.get(date_format, 'MM/dd/yyyy')
        date_text = current_date.toString(qt_format)
        self.date_label.setText(date_text)

    def attempt_unlock(self):
        """Attempt to unlock the screen with the provided password."""
        if self.locked_out:
            self.error_label.setText("Account locked. Please wait.")
            self.error_label.show()
            return

        password = self.password_field.text()
        stored_password = self.settings.get('password', '')

        if self.settings.get('hash_passwords', True):
            # Compare hashed passwords
            hashed_input = hashlib.sha256(password.encode()).hexdigest()
            if hashed_input == stored_password:
                self.unlock()
            else:
                self.handle_failed_attempt()
        else:
            # Compare plain text passwords
            if password == stored_password:
                self.unlock()
            else:
                self.handle_failed_attempt()

    def handle_failed_attempt(self):
        """Handle failed login attempt."""
        self.failed_attempts += 1
        max_attempts = self.settings.get('max_attempts', 3)

        if self.failed_attempts >= max_attempts:
            # Lock out the account
            self.locked_out = True
            lockout_duration = self.settings.get('lockout_duration', 5) * 60000  # Convert to milliseconds

            self.error_label.setText(f"Too many failed attempts. Locked for {self.settings.get('lockout_duration', 5)} minutes.")
            self.error_label.show()

            self.password_field.setEnabled(False)
            self.unlock_button.setEnabled(False)

            # Start lockout timer
            self.lockout_timer = QTimer(self)
            self.lockout_timer.timeout.connect(self.end_lockout)
            self.lockout_timer.setSingleShot(True)
            self.lockout_timer.start(lockout_duration)
        else:
            # Show error message
            remaining = max_attempts - self.failed_attempts
            self.error_label.setText(f"Incorrect password. {remaining} attempts remaining.")
            self.error_label.show()

        # Clear password field
        self.password_field.clear()

    def end_lockout(self):
        """End the lockout period."""
        self.locked_out = False
        self.failed_attempts = 0
        self.password_field.setEnabled(True)
        self.unlock_button.setEnabled(True)
        self.error_label.hide()

    def unlock(self):
        """Unlock the screen."""
        self.unlocked.emit()
        self.hide()

    def load_settings(self):
        """Load settings from JSON file."""
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading settings: {e}")
            return {}

    def check_inactivity(self):
        """Check for user inactivity."""
        current_time = QtCore.QDateTime.currentDateTime()
        timeout = self.settings.get('timeout', 5) * 60  # Convert to seconds

        # Check if the timeout has elapsed
        if self.last_activity_time.secsTo(current_time) > timeout:
            # Reset the timer
            self.last_activity_time = current_time
            # Just for demonstration, in a real app you'd lock the screen here
            print("Screen would lock due to inactivity")

    def load_slideshow_images(self):
        """Load slideshow images from the specified folder."""
        folder = self.settings.get('slideshow_folder', '')
        if folder and os.path.isdir(folder):
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
            self.wallpaper_files = [
                os.path.join(folder, f) for f in os.listdir(folder)
                if os.path.splitext(f)[1].lower() in image_extensions
            ]

    def change_wallpaper(self):
        """Change the wallpaper for slideshow."""
        if self.wallpaper_files:
            random_wallpaper = random.choice(self.wallpaper_files)
            self.settings['wallpaper'] = random_wallpaper
            self.set_background()

    def mouseMoveEvent(self, event):
        """Handle mouse movement events."""
        # Update the last activity time
        self.last_activity_time = QtCore.QDateTime.currentDateTime()

        # Check for hot corners
        if self.settings.get('hot_corners', False):
            pos = event.pos()
            screen_rect = QtWidgets.QApplication.desktop().screenGeometry()

            # Define corner areas (20x20 pixels in each corner)
            corners = [
                QtCore.QRect(0, 0, 20, 20),  # Top-left
                QtCore.QRect(screen_rect.width() - 20, 0, 20, 20),  # Top-right
                QtCore.QRect(0, screen_rect.height() - 20, 20, 20),  # Bottom-left
                QtCore.QRect(screen_rect.width() - 20, screen_rect.height() - 20, 20, 20)  # Bottom-right
            ]

            # Check if mouse is in any corner
            for corner in corners:
                if corner.contains(pos):
                    print("Hot corner detected - preventing screen lock")
                    self.last_activity_time = QtCore.QDateTime.currentDateTime()
                    break

        super().mouseMoveEvent(event)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    try:
        print("Starting Lock Screen Settings...")
        settings = SettingsPanel()
        settings.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error launching settings: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        app.quit()
