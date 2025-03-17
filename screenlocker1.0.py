import platform
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QCheckBox, QSpinBox, QComboBox, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QCursor,QIcon
import json
import os
import sys
import hashlib
import random
import string

import platform
if platform.system() == "Windows":
    import win32api
    import win32con
    import win32gui
    import win32process
elif platform.system() == "Darwin":  # macOS
    import subprocess
elif platform.system() == "Linux":
    import subprocess

class SettingsPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lock Screen Settings")
        self.setMinimumSize(500, 700)
        self.settings = self.load_settings()
        # Initialize system sleep detection
        self.init_system_sleep_detection()
        # Initialize lock screen integration
        self.initialize_lock_screen_integration()
        self.disable_windows_lock_screen()
        self.prevent_system_lock()
        # Initialize general layout
        self.general_layout = QtWidgets.QVBoxLayout()
        self.init_custom_lock_screen_settings()
        self.override_system_lock_events()
        # Initialize system tray
        self.init_system_tray()

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

        # Auto lock when user is away (webcam detection)
        self.webcam_detection_checkbox = QtWidgets.QCheckBox("Enable webcam presence detection")
        self.webcam_detection_checkbox.setChecked(self.settings.get('webcam_detection', False))
        self.webcam_detection_checkbox.setToolTip("Use webcam to detect if user is away and lock screen automatically.")
        general_layout.addWidget(self.webcam_detection_checkbox)
        
        # Webcam detection sensitivity
        webcam_sensitivity_layout = QtWidgets.QHBoxLayout()
        webcam_sensitivity_label = QtWidgets.QLabel("Webcam detection sensitivity:")
        self.webcam_sensitivity_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.webcam_sensitivity_slider.setRange(1, 10)
        self.webcam_sensitivity_slider.setValue(self.settings.get('webcam_sensitivity', 5))
        self.webcam_sensitivity_slider.setToolTip("Adjust the sensitivity of webcam detection.")
        webcam_sensitivity_layout.addWidget(webcam_sensitivity_label)
        webcam_sensitivity_layout.addWidget(self.webcam_sensitivity_slider)
        general_layout.addLayout(webcam_sensitivity_layout)

        # Auto start with system
        self.autostart_checkbox = QtWidgets.QCheckBox("Start application with system")
        self.autostart_checkbox.setChecked(self.settings.get('autostart', False))
        self.autostart_checkbox.setToolTip("Application will start automatically when the system boots.")
        general_layout.addWidget(self.autostart_checkbox)

        # Show in system tray
        self.system_tray_checkbox = QtWidgets.QCheckBox("Show in system tray")
        self.system_tray_checkbox.setChecked(self.settings.get('system_tray', True))
        self.system_tray_checkbox.setToolTip("Show application icon in system tray for quick access.")
        general_layout.addWidget(self.system_tray_checkbox)

        # Minimize to tray instead of taskbar
        self.minimize_to_tray_checkbox = QtWidgets.QCheckBox("Minimize to tray instead of taskbar")
        self.minimize_to_tray_checkbox.setChecked(self.settings.get('minimize_to_tray', False))
        self.minimize_to_tray_checkbox.setToolTip("Application will minimize to system tray instead of taskbar.")
        general_layout.addWidget(self.minimize_to_tray_checkbox)

        general_tab.setLayout(general_layout)

        # --- Security Tab ---
        security_tab = QtWidgets.QWidget()
        security_layout = QtWidgets.QVBoxLayout()

        # Password configuration
        password_group = QtWidgets.QGroupBox("Password Configuration")
        password_layout = QtWidgets.QFormLayout()

        # Authentication method
        auth_method_label = QtWidgets.QLabel("Authentication Method:")
        self.auth_method_combo = QtWidgets.QComboBox()
        self.auth_method_combo.addItems(["Password", "PIN", "Pattern", "Biometric"])
        self.auth_method_combo.setCurrentText(self.settings.get('auth_method', 'Password'))
        self.auth_method_combo.currentTextChanged.connect(self.update_auth_method)
        password_layout.addRow(auth_method_label, self.auth_method_combo)

        # Password settings
        self.password_widget = QtWidgets.QWidget()
        password_inner_layout = QtWidgets.QFormLayout()
        self.password_widget.setLayout(password_inner_layout)

        self.password_field = QtWidgets.QLineEdit()
        self.password_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_field.setText(self.settings.get('password', ''))
        password_inner_layout.addRow("New Password:", self.password_field)

        self.confirm_password_field = QtWidgets.QLineEdit()
        self.confirm_password_field.setEchoMode(QtWidgets.QLineEdit.Password)
        password_inner_layout.addRow("Confirm Password:", self.confirm_password_field)

        # Password strength indicator
        self.password_strength_label = QtWidgets.QLabel("Password Strength: ")
        self.password_strength_indicator = QtWidgets.QProgressBar()
        self.password_strength_indicator.setRange(0, 100)
        self.password_strength_indicator.setValue(0)
        self.password_field.textChanged.connect(self.update_password_strength)
        password_inner_layout.addRow(self.password_strength_label, self.password_strength_indicator)

        # Password generation
        generate_password_button = QtWidgets.QPushButton("Generate Strong Password")
        generate_password_button.clicked.connect(self.generate_strong_password)
        password_inner_layout.addRow(generate_password_button)

        # PIN settings
        self.pin_widget = QtWidgets.QWidget()
        pin_inner_layout = QtWidgets.QFormLayout()
        self.pin_widget.setLayout(pin_inner_layout)
        self.pin_widget.setVisible(False)

        self.pin_field = QtWidgets.QLineEdit()
        self.pin_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pin_field.setValidator(QtGui.QIntValidator())
        self.pin_field.setText(self.settings.get('pin', ''))
        pin_inner_layout.addRow("New PIN:", self.pin_field)

        self.confirm_pin_field = QtWidgets.QLineEdit()
        self.confirm_pin_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirm_pin_field.setValidator(QtGui.QIntValidator())
        pin_inner_layout.addRow("Confirm PIN:", self.confirm_pin_field)

        # PIN length configuration
        pin_length_layout = QtWidgets.QHBoxLayout()
        pin_length_label = QtWidgets.QLabel("PIN Length:")
        self.pin_length_combo = QtWidgets.QComboBox()
        self.pin_length_combo.addItems(["4", "6", "8"])
        self.pin_length_combo.setCurrentText(str(self.settings.get('pin_length', 4)))
        pin_length_layout.addWidget(pin_length_label)
        pin_length_layout.addWidget(self.pin_length_combo)
        pin_inner_layout.addRow(pin_length_layout)

        # Pattern settings
        self.pattern_widget = QtWidgets.QWidget()
        pattern_inner_layout = QtWidgets.QVBoxLayout()
        self.pattern_widget.setLayout(pattern_inner_layout)
        self.pattern_widget.setVisible(False)

        pattern_label = QtWidgets.QLabel("Draw Pattern:")
        pattern_inner_layout.addWidget(pattern_label)
        
        # Pattern grid size
        pattern_grid_layout = QtWidgets.QHBoxLayout()
        pattern_grid_label = QtWidgets.QLabel("Pattern Grid Size:")
        self.pattern_grid_combo = QtWidgets.QComboBox()
        self.pattern_grid_combo.addItems(["3x3", "4x4", "5x5"])
        self.pattern_grid_combo.setCurrentText(self.settings.get('pattern_grid', '3x3'))
        pattern_grid_layout.addWidget(pattern_grid_label)
        pattern_grid_layout.addWidget(self.pattern_grid_combo)
        pattern_inner_layout.addLayout(pattern_grid_layout)
        
        # Pattern display placeholder
        self.pattern_display = QtWidgets.QLabel("Pattern setup requires GUI implementation")
        self.pattern_display.setAlignment(QtCore.Qt.AlignCenter)
        self.pattern_display.setStyleSheet("border: 1px solid #555;")
        self.pattern_display.setMinimumHeight(150)
        pattern_inner_layout.addWidget(self.pattern_display)

        # Biometric settings
        self.biometric_widget = QtWidgets.QWidget()
        biometric_inner_layout = QtWidgets.QVBoxLayout()
        self.biometric_widget.setLayout(biometric_inner_layout)
        self.biometric_widget.setVisible(False)

        # Biometric options
        self.fingerprint_checkbox = QtWidgets.QCheckBox("Use Fingerprint")
        self.fingerprint_checkbox.setChecked(self.settings.get('use_fingerprint', False))
        biometric_inner_layout.addWidget(self.fingerprint_checkbox)

        self.face_recognition_checkbox = QtWidgets.QCheckBox("Use Face Recognition")
        self.face_recognition_checkbox.setChecked(self.settings.get('use_face_recognition', False))
        biometric_inner_layout.addWidget(self.face_recognition_checkbox)

        self.face_recognition_accuracy = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.face_recognition_accuracy.setRange(1, 10)
        self.face_recognition_accuracy.setValue(self.settings.get('face_recognition_accuracy', 7))
        biometric_inner_layout.addWidget(QtWidgets.QLabel("Face Recognition Accuracy:"))
        biometric_inner_layout.addWidget(self.face_recognition_accuracy)

        # Add auth method widgets
        password_layout.addRow(self.password_widget)
        password_layout.addRow(self.pin_widget)
        password_layout.addRow(self.pattern_widget)
        password_layout.addRow(self.biometric_widget)

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

        # Two factor method
        two_factor_method_layout = QtWidgets.QHBoxLayout()
        two_factor_method_label = QtWidgets.QLabel("2FA Method:")
        self.two_factor_method_combo = QtWidgets.QComboBox()
        self.two_factor_method_combo.addItems(["Email", "SMS", "Authenticator App"])
        self.two_factor_method_combo.setCurrentText(self.settings.get('two_factor_method', 'Email'))
        two_factor_method_layout.addWidget(two_factor_method_label)
        two_factor_method_layout.addWidget(self.two_factor_method_combo)
        password_layout.addRow(two_factor_method_layout)

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

        password_group.setLayout(password_layout)
        security_layout.addWidget(password_group)

        # Emergency access settings
        emergency_group = QtWidgets.QGroupBox("Emergency Access")
        emergency_layout = QtWidgets.QVBoxLayout()

        # Recovery email
        recovery_email_layout = QtWidgets.QHBoxLayout()
        recovery_email_label = QtWidgets.QLabel("Recovery Email:")
        self.recovery_email_field = QtWidgets.QLineEdit()
        self.recovery_email_field.setText(self.settings.get('recovery_email', ''))
        recovery_email_layout.addWidget(recovery_email_label)
        recovery_email_layout.addWidget(self.recovery_email_field)
        emergency_layout.addLayout(recovery_email_layout)

        # Recovery questions
        self.recovery_questions_checkbox = QtWidgets.QCheckBox("Enable recovery questions")
        self.recovery_questions_checkbox.setChecked(self.settings.get('use_recovery_questions', False))
        emergency_layout.addWidget(self.recovery_questions_checkbox)

        emergency_group.setLayout(emergency_layout)
        security_layout.addWidget(emergency_group)

        security_tab.setLayout(security_layout)

        # --- Appearance Tab ---
        appearance_tab = QtWidgets.QWidget()
        appearance_layout = QtWidgets.QVBoxLayout()

        # Background configuration
        background_group = QtWidgets.QGroupBox("Background")
        background_layout = QtWidgets.QVBoxLayout()

        # Background type
        background_type_layout = QtWidgets.QHBoxLayout()
        background_type_label = QtWidgets.QLabel("Background Type:")
        self.background_type_combo = QtWidgets.QComboBox()
        self.background_type_combo.addItems(["Solid Color", "Image", "Slideshow"])
        self.background_type_combo.setCurrentText(self.settings.get('background_type', 'Solid Color'))
        background_type_layout.addWidget(background_type_label)
        background_type_layout.addWidget(self.background_type_combo)
        background_layout.addLayout(background_type_layout)

        # Background color picker
        background_color_layout = QtWidgets.QHBoxLayout()
        background_color_label = QtWidgets.QLabel("Background Color:")
        self.background_color_button = QtWidgets.QPushButton()
        self.background_color_button.setFixedSize(30, 30)
        self.set_button_color(self.background_color_button, self.settings.get('background_color', '#000000'))
        self.background_color_button.clicked.connect(self.pick_background_color)
        background_color_layout.addWidget(background_color_label)
        background_color_layout.addWidget(self.background_color_button)
        background_layout.addLayout(background_color_layout)

        # Background image selection
        background_image_layout = QtWidgets.QHBoxLayout()
        background_image_label = QtWidgets.QLabel("Background Image:")
        self.background_image_path = QtWidgets.QLineEdit()
        self.background_image_path.setText(self.settings.get('background_image', ''))
        self.background_image_browse = QtWidgets.QPushButton("Browse")
        self.background_image_browse.clicked.connect(self.browse_background_image)
        background_image_layout.addWidget(background_image_label)
        background_image_layout.addWidget(self.background_image_path)
        background_image_layout.addWidget(self.background_image_browse)
        background_layout.addLayout(background_image_layout)

        background_group.setLayout(background_layout)
        appearance_layout.addWidget(background_group)

        # Clock configuration
        clock_group = QtWidgets.QGroupBox("Clock")
        clock_layout = QtWidgets.QVBoxLayout()

        # Show clock
        self.show_clock_checkbox = QtWidgets.QCheckBox("Show Clock")
        self.show_clock_checkbox.setChecked(self.settings.get('show_clock', True))
        clock_layout.addWidget(self.show_clock_checkbox)

        # Clock format
        clock_format_layout = QtWidgets.QHBoxLayout()
        clock_format_label = QtWidgets.QLabel("Clock Format:")
        self.clock_format_combo = QtWidgets.QComboBox()
        self.clock_format_combo.addItems(["12-hour", "24-hour"])
        self.clock_format_combo.setCurrentText(self.settings.get('clock_format', '24-hour'))
        clock_format_layout.addWidget(clock_format_label)
        clock_format_layout.addWidget(self.clock_format_combo)
        clock_layout.addLayout(clock_format_layout)

        clock_group.setLayout(clock_layout)
        appearance_layout.addWidget(clock_group)

        appearance_tab.setLayout(appearance_layout)

        # Add all tabs to the tab widget
        self.tab_widget.addTab(general_tab, "General")
        self.tab_widget.addTab(security_tab, "Security")
        self.tab_widget.addTab(appearance_tab, "Appearance")

        # Add the tab widget to the main layout
        layout.addWidget(self.tab_widget)

        # Save and Cancel buttons
        buttons_layout = QtWidgets.QHBoxLayout()
        self.save_button = QtWidgets.QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)
        
        # Apply the current settings
        self.apply_theme()
        self.update_auth_method()

    def init_custom_lock_screen_settings(self):
        """
        Add settings for custom lock screen and system lock screen override.
        """
        custom_lock_layout = QtWidgets.QHBoxLayout()
        self.custom_lock_checkbox = QtWidgets.QCheckBox("Use Custom Lock Screen")
        self.custom_lock_checkbox.setChecked(self.settings.get('custom_lock', True))
        self.custom_lock_checkbox.stateChanged.connect(self.toggle_custom_lock)
        custom_lock_layout.addWidget(self.custom_lock_checkbox)
        self.general_layout.addLayout(custom_lock_layout)

    def toggle_custom_lock(self):
        """
        Toggle custom lock screen and override system lock screen.
        """
        enable = self.custom_lock_checkbox.isChecked()
        if enable:
            self.disable_windows_lock_screen()
            self.prevent_system_lock()
            if not self.override_system_lock_events():
                print("Failed to override system lock events. Falling back to default behavior.")
        self.settings['custom_lock'] = enable


    def initialize_lock_screen_integration(self):
        """
        Initialize all lock screen integration features.
        """
        try:
            # Configure auto-start
            self.configure_autostart(True)
            print("Auto-start configured.")

            # Set up sleep detection
            self.init_system_sleep_detection()
            print("Sleep detection initialized.")

            # Set as default lock screen on Windows
            if platform.system() == "Windows":
                self.set_as_default_lock_screen()
                print("Custom lock screen set as default on Windows.")
            else:
                print(f"Default lock screen override not supported on {platform.system()}.")

        except Exception as e:
            print(f"Failed to initialize lock screen integration: {e}")

    def prevent_system_lock(self):
        """
        Prevent the system from locking or going to sleep.
        """
        import ctypes

        # Constants for SetThreadExecutionState
        ES_CONTINUOUS = 0x80000000
        ES_SYSTEM_REQUIRED = 0x00000001
        ES_DISPLAY_REQUIRED = 0x00000002

        try:
            # Prevent system sleep and display turn-off
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
            print("System lock and sleep prevented.")
        except Exception as e:
            print(f"Failed to prevent system lock: {e}")

    def load_settings(self):
        # Load settings from a JSON file
        try:
            with open('settings.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default settings if file doesn't exist
            return {
                'theme': 'Dark',
                'timeout': 5,
                'hot_corners': False,
                'lock_on_startup': False,
                'lock_on_sleep': True,
                'webcam_detection': False,
                'webcam_sensitivity': 5,
                'autostart': False,
                'system_tray': True,
                'minimize_to_tray': False,
                'auth_method': 'Password',
                'password': '',
                'pin': '',
                'pin_length': 4,
                'pattern_grid': '3x3',
                'use_fingerprint': False,
                'use_face_recognition': False,
                'face_recognition_accuracy': 7,
                'hash_passwords': True,
                'two_factor': False,
                'two_factor_method': 'Email',
                'max_attempts': 3,
                'lockout_duration': 5,
                'recovery_email': '',
                'use_recovery_questions': False,
                'background_type': 'Solid Color',
                'background_color': '#000000',
                'background_image': '',
                'show_clock': True,
                'clock_format': '24-hour'
            }

    def save_settings(self):
        # Validate settings before saving
        if not self.validate_settings():
            return

        # Get all settings from UI
        settings = {
            'theme': self.theme_combo.currentText(),
            'timeout': self.timeout_spinbox.value(),
            'hot_corners': self.hot_corners_checkbox.isChecked(),
            'lock_on_startup': self.lock_on_startup_checkbox.isChecked(),
            'lock_on_sleep': self.lock_on_sleep_checkbox.isChecked(),
            'webcam_detection': self.webcam_detection_checkbox.isChecked(),
            'webcam_sensitivity': self.webcam_sensitivity_slider.value(),
            'autostart': self.autostart_checkbox.isChecked(),
            'system_tray': self.system_tray_checkbox.isChecked(),
            'minimize_to_tray': self.minimize_to_tray_checkbox.isChecked(),
            'auth_method': self.auth_method_combo.currentText(),
            'hash_passwords': self.hash_passwords_checkbox.isChecked(),
            'two_factor': self.two_factor_checkbox.isChecked(),
            'two_factor_method': self.two_factor_method_combo.currentText(),
            'max_attempts': self.max_attempts_spinbox.value(),
            'lockout_duration': self.lockout_spinbox.value(),
            'recovery_email': self.recovery_email_field.text(),
            'use_recovery_questions': self.recovery_questions_checkbox.isChecked(),
            'background_type': self.background_type_combo.currentText(),
            'background_color': self.get_button_color(self.background_color_button),
            'background_image': self.background_image_path.text(),
            'show_clock': self.show_clock_checkbox.isChecked(),
            'clock_format': self.clock_format_combo.currentText()
        }

        # Save authentication method specific settings
        auth_method = self.auth_method_combo.currentText()
        if auth_method == "Password":
            # Store password (hashed if enabled)
            if self.password_field.text():
                if self.hash_passwords_checkbox.isChecked():
                    settings['password'] = self.hash_password(self.password_field.text())
                else:
                    settings['password'] = self.password_field.text()
        elif auth_method == "PIN":
            settings['pin'] = self.pin_field.text()
            settings['pin_length'] = int(self.pin_length_combo.currentText())
        elif auth_method == "Pattern":
            settings['pattern_grid'] = self.pattern_grid_combo.currentText()
            # Pattern data would be stored here
        elif auth_method == "Biometric":
            settings['use_fingerprint'] = self.fingerprint_checkbox.isChecked()
            settings['use_face_recognition'] = self.face_recognition_checkbox.isChecked()
            settings['face_recognition_accuracy'] = self.face_recognition_accuracy.value()

        # Save settings to file
        with open('settings.json', 'w') as f:
            json.dump(settings, f, indent=2)

        # Apply settings
        self.settings = settings
        self.apply_settings()
        
        # Show success message
        QtWidgets.QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully.")

    def init_system_tray(self):
        """Initialize the system tray icon and menu."""
        # Create the system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        
        # Create an emoji icon (lock emoji)
        font = QtGui.QFont()
        font.setPointSize(14)
        
        pixmap = QtGui.QPixmap(32, 32)
        pixmap.fill(QtGui.QColor(0, 0, 0, 0))  # Transparent background
        
        painter = QtGui.QPainter(pixmap)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), QtCore.Qt.AlignCenter, "🔒")  # Lock emoji
        painter.end()
        
        icon = QtGui.QIcon(pixmap)
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("Screen Lock")
        
        # Create a context menu for the tray icon
        self.tray_menu = QMenu()
        
        # Add "Lock Screen" action
        lock_action = QAction("🔒 Lock Screen", self)
        lock_action.triggered.connect(self.lock_screen)
        self.tray_menu.addAction(lock_action)
        
        # Add "Settings" action
        settings_action = QAction("⚙️ Settings", self)
        settings_action.triggered.connect(self.show)
        self.tray_menu.addAction(settings_action)
        
        # Add a separator
        self.tray_menu.addSeparator()
        
        # Add "Quit" action
        quit_action = QAction("❌ Quit", self)
        quit_action.triggered.connect(QtWidgets.QApplication.quit)
        self.tray_menu.addAction(quit_action)
        
        # Set the context menu to the tray icon
        self.tray_icon.setContextMenu(self.tray_menu)
        
        # Show the tray icon
        self.tray_icon.show()
        
        # Connect the tray icon's activated signal (e.g., double-click)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    def on_tray_icon_activated(self, reason):
        """Handle tray icon activation (e.g., double-click)."""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()  # Show the settings window on double-click

    def lock_screen(self):
        """Activate the screen lock."""
        try:
            if self.screen_lock is not None:
                self.screen_lock.close()
            
            self.screen_lock = LockScreen(self.settings)
            self.screen_lock.unlocked.connect(self.on_unlock)
            self.screen_lock.show()
            
            # Show a notification when the screen locks
            self.tray_icon.showMessage(
                "🔒 Screen Locked",
                "Your screen has been locked.",
                QSystemTrayIcon.Information,
                2000  # Display for 2 seconds
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to activate screen lock: {e}")

    def on_unlock(self):
        """Handle the unlocked signal from the lock screen."""
        # Show a notification when the screen unlocks
        self.tray_icon.showMessage(
            "🔓 Screen Unlocked",
            "Your screen has been unlocked.",
            QSystemTrayIcon.Information,
            2000  # Display for 2 seconds
        )
        
        # Optionally, perform other actions (e.g., reset timers, update UI)
        self.reset_inactivity_timer()


    def validate_settings(self):
        # Validate password fields
        if self.auth_method_combo.currentText() == "Password" and self.password_field.text():
            if self.password_field.text() != self.confirm_password_field.text():
                QtWidgets.QMessageBox.warning(self, "Password Mismatch", "Passwords do not match.")
                return False
        
        # Validate PIN fields
        if self.auth_method_combo.currentText() == "PIN" and self.pin_field.text():
            if self.pin_field.text() != self.confirm_pin_field.text():
                QtWidgets.QMessageBox.warning(self, "PIN Mismatch", "PINs do not match.")
                return False
            
            pin_length = int(self.pin_length_combo.currentText())
            if len(self.pin_field.text()) != pin_length:
                QtWidgets.QMessageBox.warning(self, "Invalid PIN", f"PIN must be {pin_length} digits long.")
                return False
        
        # Validate email format
        if self.recovery_email_field.text():
            if not self.is_valid_email(self.recovery_email_field.text()):
                QtWidgets.QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address.")
                return False
        
        return True

    def is_valid_email(self, email):
        # Simple email validation
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def hash_password(self, password):
        # Simple password hashing with SHA-256
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

    def apply_settings(self):
        # Apply the current settings
        self.apply_theme()
        self.reset_inactivity_timer()
        
        # Configure autostart
        self.configure_autostart(self.settings.get('autostart', False))
        
        # Configure system tray
        if not self.settings.get('system_tray', True):
            # Code to hide system tray icon
            pass

    def apply_theme(self):
        theme = self.theme_combo.currentText()
        if theme == "Light":
            self.setStyleSheet("""
                QWidget { background-color: #f0f0f0; color: #000000; }
                QPushButton { background-color: #e0e0e0; border: 1px solid #c0c0c0; padding: 5px; }
                QPushButton:hover { background-color: #d0d0d0; }
                QLineEdit, QSpinBox, QComboBox { background-color: #ffffff; border: 1px solid #c0c0c0; padding: 5px; }
            """)
        elif theme == "Dark":
            self.setStyleSheet("""
                QWidget { background-color: #2d2d2d; color: #ffffff; }
                QPushButton { background-color: #3d3d3d; border: 1px solid #505050; padding: 5px; }
                QPushButton:hover { background-color: #4d4d4d; }
                QLineEdit, QSpinBox, QComboBox { background-color: #3d3d3d; border: 1px solid #505050; padding: 5px; color: #ffffff; }
                QTabWidget::pane { border: 1px solid #505050; }
                QTabBar::tab { background-color: #3d3d3d; color: #ffffff; padding: 8px 16px; }
                QTabBar::tab:selected { background-color: #505050; }
            """)
        # Custom theme implementation would go here

    def update_auth_method(self):
        method = self.auth_method_combo.currentText()
        
        # Hide all auth method widgets first
        self.password_widget.setVisible(False)
        self.pin_widget.setVisible(False)
        self.pattern_widget.setVisible(False)
        self.biometric_widget.setVisible(False)
        
        # Show the selected auth method widget
        if method == "Password":
            self.password_widget.setVisible(True)
        elif method == "PIN":
            self.pin_widget.setVisible(True)
        elif method == "Pattern":
            self.pattern_widget.setVisible(True)
        elif method == "Biometric":
            self.biometric_widget.setVisible(True)

    def update_password_strength(self):
        password = self.password_field.text()
        strength = self.calculate_password_strength(password)
        self.password_strength_indicator.setValue(strength)
        
        if strength < 30:
            self.password_strength_label.setText("Password Strength: Weak")
            self.password_strength_indicator.setStyleSheet("QProgressBar::chunk { background-color: red; }")
        elif strength < 60:
            self.password_strength_label.setText("Password Strength: Medium")
            self.password_strength_indicator.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
        else:
            self.password_strength_label.setText("Password Strength: Strong")
            self.password_strength_indicator.setStyleSheet("QProgressBar::chunk { background-color: green; }")

    def calculate_password_strength(self, password):
        # Calculate password strength (0-100)
        if not password:
            return 0
            
        strength = 0
        
        # Length check
        if len(password) >= 8:
            strength += 25
        elif len(password) >= 6:
            strength += 10
            
        # Character variety checks
        if any(c.islower() for c in password):
            strength += 10
        if any(c.isupper() for c in password):
            strength += 15
        if any(c.isdigit() for c in password):
            strength += 15
        if any(not c.isalnum() for c in password):
            strength += 20
            
        # Penalize common patterns
        common_patterns = ['123', 'abc', 'qwerty', 'password', 'admin']
        lower_password = password.lower()
        for pattern in common_patterns:
            if pattern in lower_password:
                strength -= 10
                
        return min(max(strength, 0), 100)
    
    def generate_strong_password(self):
        """Generate a strong password and populate the password fields."""
        # Define character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"

        # Combine all character sets
        all_chars = lowercase + uppercase + digits + symbols

        # Generate a 12-character password
        password = ''.join(random.choice(all_chars) for _ in range(12))

        # Populate the password fields
        self.password_field.setText(password)
        self.confirm_password_field.setText(password)

        # Update password strength indicator
        self.update_password_strength()
    
    def pick_background_color(self):
        color = QtWidgets.QColorDialog.getColor(QtGui.QColor(self.get_button_color(self.background_color_button)))
        if color.isValid():
            self.set_button_color(self.background_color_button, color.name())
    
    def set_button_color(self, button, color_code):
        button.setStyleSheet(f"background-color: {color_code};")
        button.setProperty("color", color_code)
    
    def get_button_color(self, button):
        return button.property("color") or "#000000"
    
    def browse_background_image(self):
        file_dialog = QtWidgets.QFileDialog()
        image_path, _ = file_dialog.getOpenFileName(
            self, "Select Background Image", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if image_path:
            self.background_image_path.setText(image_path)

    def configure_autostart(self, enable):
        """
        Configure auto-start on system boot for Windows, macOS, and Linux.
        """
        import platform
        import os
        import sys
        import subprocess
        system = platform.system()
        app_path = os.path.abspath(sys.argv[0])
        try:
            if system == "Windows":
                self._configure_autostart_windows(enable, app_path)
            elif system == "Darwin":  # macOS
                self._configure_autostart_macos(enable, app_path)
            elif system == "Linux":
                self._configure_autostart_linux(enable, app_path)
            else:
                print(f"Auto-start not supported on {system}")
        except Exception as e:
            print(f"Failed to configure auto-start: {e}")

    def _configure_autostart_windows(self, enable, app_path):
        """
        Configure auto-start on Windows using the registry.
        """
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                if enable:
                    winreg.SetValueEx(key, "ScreenLocker", 0, winreg.REG_SZ, app_path)
                else:
                    try:
                        winreg.DeleteValue(key, "ScreenLocker")
                    except FileNotFoundError:
                        pass  # Key doesn't exist
        except Exception as e:
            raise Exception(f"Windows registry error: {e}")

    def _configure_autostart_macos(self, enable, app_path):
        """
        Configure auto-start on macOS using a launch agent.
        """
        import os
        import subprocess
        plist_path = os.path.expanduser("~/Library/LaunchAgents/com.screenlocker.plist")
        if enable:
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
            <plist version="1.0">
            <dict>
                <key>Label</key>
                <string>com.screenlocker</string>
                <key>ProgramArguments</key>
                <array>
                    <string>{app_path}</string>
                </array>
                <key>RunAtLoad</key>
                <true/>
            </dict>
            </plist>"""
            
            os.makedirs(os.path.dirname(plist_path), exist_ok=True)
            with open(plist_path, 'w') as f:
                f.write(plist_content)
            subprocess.run(["launchctl", "load", plist_path], check=True)
        else:
            if os.path.exists(plist_path):
                subprocess.run(["launchctl", "unload", plist_path], check=True)
                os.remove(plist_path)

    def _configure_autostart_linux(self, enable, app_path):
        """
        Configure auto-start on Linux using a .desktop file.
        """
        import os
        autostart_dir = os.path.expanduser("~/.config/autostart")
        desktop_file = os.path.join(autostart_dir, "screenlocker.desktop")
        if enable:
            desktop_content = f"""[Desktop Entry]
            Type=Application
            Name=Screen Locker
            Exec={app_path}
            Terminal=false
            X-GNOME-Autostart-enabled=true
            """
            
            os.makedirs(autostart_dir, exist_ok=True)
            with open(desktop_file, 'w') as f:
                f.write(desktop_content)
        else:
            if os.path.exists(desktop_file):
                os.remove(desktop_file)

    def init_system_sleep_detection(self):
        """
        Initialize system sleep/hibernate detection based on the OS.
        """
        import platform
        system = platform.system()
        try:
            if system == "Windows":
                self.init_windows_sleep_detection()
            elif system == "Darwin":  # macOS
                self.init_macos_sleep_detection()
            elif system == "Linux":
                self.init_linux_sleep_detection()
            else:
                print(f"Sleep detection not supported on {system}")
        except Exception as e:
            print(f"Failed to initialize sleep detection: {e}")

    def init_windows_sleep_detection(self):
        """
        Detect sleep/hibernate events on Windows using win32api.
        """
        import win32api
        import win32con
        import win32gui
        
        def wnd_proc(hwnd, msg, wparam, lparam):
            if msg == win32con.WM_POWERBROADCAST:
                if wparam == win32con.PBT_APMSUSPEND:
                    print("System is suspending (sleeping)...")
                    self.lock_screen()
                elif wparam == win32con.PBT_APMRESUMESUSPEND:
                    print("System has resumed from sleep...")
            return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
        
        # Create a hidden window to listen for power events
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = wnd_proc
        wc.lpszClassName = "LockScreenPowerListener"
        wc.hInstance = win32api.GetModuleHandle(None)
        class_atom = win32gui.RegisterClass(wc)
        
        # Create the window
        self.hwnd = win32gui.CreateWindow(
            class_atom,  # Class atom
            "LockScreenPowerListener",  # Window name
            0,  # Window style
            0,  # X position
            0,  # Y position
            0,  # Width
            0,  # Height
            0,  # Parent window
            0,  # Menu
            wc.hInstance,  # Instance handle
            None  # Additional data
        )
        
        if not self.hwnd:
            raise Exception("Failed to create hidden window for sleep detection.")

    def init_macos_sleep_detection(self):
        """
        Detect sleep events on macOS using pmset.
        """
        import subprocess
        import threading
        
        def listen_for_sleep():
            process = subprocess.Popen(["pmset", "-g", "log"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            while True:
                output = process.stdout.readline()
                if output == "" and process.poll() is not None:
                    break
                if "System Sleep" in output:
                    print("System is sleeping...")
                    self.lock_screen()
                elif "Wake" in output:
                    print("System has woken up...")
        
        threading.Thread(target=listen_for_sleep, daemon=True).start()

    def init_linux_sleep_detection(self):
        """
        Detect sleep events on Linux using systemd or dbus.
        """
        import subprocess
        import threading
        
        def listen_for_sleep():
            process = subprocess.Popen(["systemctl", "suspend"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            while True:
                output = process.stdout.readline()
                if output == "" and process.poll() is not None:
                    break
                if "Sleep" in output:
                    print("System is sleeping...")
                    self.lock_screen()
                elif "Wake" in output:
                    print("System has woken up...")
        
        threading.Thread(target=listen_for_sleep, daemon=True).start()

    def set_as_default_lock_screen(self):
        """
        Set this application as the default Windows lock screen.
        This includes disabling the Windows lock screen and overriding the Win+L keyboard shortcut.
        """
        import platform
        system = platform.system()
        
        if system == "Windows":
            self.disable_windows_lock_screen()
            self.override_system_lock_events()
        else:
            print(f"Setting as default lock screen not supported on {system}")

    def disable_windows_lock_screen(self):
        """
        Disable the default Windows lock screen by modifying the registry.
        Requires administrative privileges.
        """
        import winreg
        import ctypes
        
        # Check if we have admin rights
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("Warning: Administrative privileges required to disable Windows lock screen.")
            return
        
        try:
            # Create the registry key if it doesn't exist
            try:
                key = winreg.CreateKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Policies\Microsoft\Windows\Personalization"
                )
            except WindowsError:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Policies\Microsoft\Windows\Personalization",
                    0, winreg.KEY_WRITE
                )
            
            # Set the value to disable the lock screen
            winreg.SetValueEx(key, "NoLockScreen", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            print("Windows lock screen disabled.")
            
            # Also disable the screen saver
            screen_saver_key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Control Panel\Desktop",
                0, winreg.KEY_WRITE
            )
            winreg.SetValueEx(screen_saver_key, "ScreenSaveActive", 0, winreg.REG_SZ, "0")
            winreg.CloseKey(screen_saver_key)
            print("Windows screen saver disabled.")
            
        except Exception as e:
            print(f"Failed to disable Windows lock screen: {e}")
            print("You may need to run this application as administrator.")

    def override_system_lock_events(self):
        """
        Override system lock events to use the custom lock screen.
        Captures the Win+L keyboard shortcut and replaces it with the custom lock screen.
        """
        import ctypes
        from ctypes import wintypes
        import threading

        # Constants for low-level hooks
        WH_KEYBOARD_LL = 13
        WM_KEYDOWN = 0x0100
        VK_LWIN = 0x5B  # Left Windows key
        VK_RWIN = 0x5C  # Right Windows key
        VK_L = 0x4C     # L key

        # Define the low-level keyboard hook callback
        def low_level_keyboard_handler(nCode, wParam, lParam):
            if nCode >= 0 and wParam == WM_KEYDOWN:
                vk_code = ctypes.cast(lParam, ctypes.POINTER(wintypes.DWORD)).contents.value & 0xFF

                # Check for Win + L (default lock screen shortcut)
                win_key_pressed = ctypes.windll.user32.GetAsyncKeyState(VK_LWIN) & 0x8000 or \
                                ctypes.windll.user32.GetAsyncKeyState(VK_RWIN) & 0x8000

                if win_key_pressed and vk_code == VK_L:
                    print("Win + L detected. Overriding system lock screen.")

                    # Schedule the lock screen on the main thread
                    threading.Thread(target=self.lock_screen).start()

                    # Block the default Windows behavior
                    return 1

            return ctypes.windll.user32.CallNextHookEx(0, nCode, wParam, lParam)

        # Convert the callback function to a C-callable function
        hook_proc_type = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
        hook_proc = hook_proc_type(low_level_keyboard_handler)

        # Keep a reference to the hook procedure to prevent garbage collection
        self.hook_proc = hook_proc

        try:
            # Set up the low-level keyboard hook
            self.hook_id = ctypes.windll.user32.SetWindowsHookExA(
                WH_KEYBOARD_LL,
                hook_proc,
                ctypes.windll.kernel32.GetModuleHandleW(None),
                0
            )

            if not self.hook_id:
                error = ctypes.windll.kernel32.GetLastError()
                print(f"Failed to set low-level keyboard hook. Error code: {error}")
                return False

            print("System lock events (Win+L) overridden.")
            return True

        except Exception as e:
            print(f"Error setting low-level keyboard hook: {e}")
            return False

    def remove_hook(self):
        """
        Remove the keyboard hook when the application exits.
        """
        if hasattr(self, 'hook_id') and self.hook_id:
            import ctypes
            ctypes.windll.user32.UnhookWindowsHookEx(self.hook_id)
            print("Keyboard hook removed.")
    
    def reset_inactivity_timer(self):
        """Reset the inactivity timer."""
        timeout_minutes = self.settings.get('timeout', 5)
        self.inactivity_timer.start(timeout_minutes * 60 * 1000)  # Convert minutes to milliseconds

    def closeEvent(self, event):
        """Handle the window close event."""
        if self.tray_icon.isVisible():
            self.tray_icon.showMessage(
                "🔒 Lock Screen",
                "The application is still running in the system tray.",
                QSystemTrayIcon.Information,
                2000  # Display for 2 seconds
            )
            self.hide()  # Hide the window instead of closing it
            event.ignore()

class LockScreen(QtWidgets.QWidget):
    unlocked = QtCore.pyqtSignal()  # Signal to emit when successfully unlocked

    def __init__(self, settings=None):
        super().__init__()
        self.setWindowTitle("Lock Screen")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        # Initialize settings and UI first
        self.settings = settings if settings else self.load_settings()
        self.failed_attempts = 0
        self.locked_out = False
        self.lockout_timer = None
        self.emoji_icons = {  # Emoji icons
            'lock': '🔒',
            'unlock': '🔓',
            'time': '🕒',
            'calendar': '📅',
            'error': '⚠️',
            'success': '✅',
            'warning': '⛔',
            'info': '💡',
            'settings': '⚙️',
            'user': '👤',
            'wait': '⏳'
        }

        # Initialize UI components first
        self.init_ui()

        # Show the window after UI is fully initialized
        self.showFullScreen()

        # Start timers and other setup
        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.timeout.connect(self.check_inactivity)
        self.inactivity_timer.start(10000)  # Check every 10 seconds

        if self.settings.get('slideshow_enabled', False):
            self.slideshow_timer = QTimer(self)
            self.slideshow_timer.timeout.connect(self.change_wallpaper)
            interval = self.settings.get('slideshow_interval', 5) * 60000  # Convert to milliseconds
            self.slideshow_timer.start(interval)
            self.wallpaper_files = []
            self.load_slideshow_images()

        if self.settings.get('hot_corners', False):
            self.setMouseTracking(True)

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

        # Lock icon
        lock_icon = QLabel(self.emoji_icons['lock'])
        lock_icon.setAlignment(QtCore.Qt.AlignCenter)
        lock_icon.setFont(QFont("Arial", 36))
        lock_icon.setStyleSheet("color: white; background-color: transparent;")
        login_layout.addWidget(lock_icon)

        # Login prompt
        login_prompt = QLabel(f"{self.emoji_icons['user']} Enter your password to unlock")
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
        self.unlock_button = QPushButton(f"{self.emoji_icons['unlock']} Unlock")
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
        
        # Add info text at the bottom
        info_label = QLabel(f"{self.emoji_icons['info']} Press ESC to force unlock (debug mode)")
        info_label.setAlignment(QtCore.Qt.AlignCenter)
        info_label.setStyleSheet("color: rgba(255, 255, 255, 0.5); background-color: transparent;")
        self.main_layout.addWidget(info_label)

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

        time_text = f"{self.emoji_icons['time']} {current_time.toString(time_format)}"
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
        date_text = f"{self.emoji_icons['calendar']} {current_date.toString(qt_format)}"
        self.date_label.setText(date_text)

    def attempt_unlock(self):
        """Attempt to unlock the screen with the provided password."""
        if self.locked_out:
            self.error_label.setText(f"{self.emoji_icons['warning']} Account locked. Please wait.")
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

            self.error_label.setText(f"{self.emoji_icons['warning']} Too many failed attempts. Locked for {self.settings.get('lockout_duration', 5)} minutes.")
            self.error_label.show()

            self.password_field.setEnabled(False)
            self.unlock_button.setEnabled(False)
            self.unlock_button.setText(f"{self.emoji_icons['wait']} Waiting...")

            # Start lockout timer
            self.lockout_timer = QTimer(self)
            self.lockout_timer.timeout.connect(self.end_lockout)
            self.lockout_timer.setSingleShot(True)
            self.lockout_timer.start(lockout_duration)
        else:
            # Show error message
            remaining = max_attempts - self.failed_attempts
            self.error_label.setText(f"{self.emoji_icons['error']} Incorrect password. {remaining} attempts remaining.")
            self.error_label.show()

        # Clear password field
        self.password_field.clear()

    def end_lockout(self):
        """End the lockout period."""
        self.locked_out = False
        self.failed_attempts = 0
        self.password_field.setEnabled(True)
        self.unlock_button.setEnabled(True)
        self.unlock_button.setText(f"{self.emoji_icons['unlock']} Unlock")
        self.error_label.hide()

    def unlock(self):
        """Unlock the screen."""
        # Show success animation or message
        self.error_label.setStyleSheet("color: #2ecc71; background-color: transparent;")
        self.error_label.setText(f"{self.emoji_icons['success']} Unlocking...")
        self.error_label.show()
        
        # Add a slight delay for better UX
        QTimer.singleShot(500, lambda: self.complete_unlock())
    
    def complete_unlock(self):
        """Complete the unlock process after animation."""
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
            print(f"{self.emoji_icons['info']} Screen would lock due to inactivity")

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
        """Handle mouse movement events for hot corners."""
        # Update last activity time
        self.last_activity_time = QtCore.QDateTime.currentDateTime()
        
        # Check for hot corners
        if self.settings.get('hot_corners', False):
            pos = event.pos()
            screen_size = QtWidgets.QApplication.desktop().screenGeometry()
            corner_size = 20  # Hot corner size in pixels
            
            # Check if mouse is in any corner
            top_left = (pos.x() <= corner_size and pos.y() <= corner_size)
            top_right = (pos.x() >= screen_size.width() - corner_size and pos.y() <= corner_size)
            bottom_left = (pos.x() <= corner_size and pos.y() >= screen_size.height() - corner_size)
            bottom_right = (pos.x() >= screen_size.width() - corner_size and pos.y() >= screen_size.height() - corner_size)
            
            # Handle hot corner actions
            if top_left and self.settings.get('top_left_action'):
                self.trigger_hot_corner_action('top_left_action')
            elif top_right and self.settings.get('top_right_action'):
                self.trigger_hot_corner_action('top_right_action')
            elif bottom_left and self.settings.get('bottom_left_action'):
                self.trigger_hot_corner_action('bottom_left_action')
            elif bottom_right and self.settings.get('bottom_right_action'):
                self.trigger_hot_corner_action('bottom_right_action')
                
        super().mouseMoveEvent(event)

    def trigger_hot_corner_action(self, corner_action):
        """Trigger the action associated with a hot corner."""
        action = self.settings.get(corner_action)
        if action == 'unlock':
            self.attempt_unlock()
        elif action == 'sleep':
            print(f"{self.emoji_icons['info']} Triggering sleep mode")
            # Implement sleep mode logic here
        elif action == 'shutdown':
            print(f"{self.emoji_icons['info']} Triggering shutdown")
            # Implement shutdown logic here
        elif action == 'restart':
            print(f"{self.emoji_icons['info']} Triggering restart")
            # Implement restart logic here
        elif action == 'screensaver':
            print(f"{self.emoji_icons['info']} Triggering screensaver")
            # Implement screensaver logic here

    def showEvent(self, event):
        """Called when the lock screen is shown."""
        super().showEvent(event)
        # Reset failed attempts
        self.failed_attempts = 0
        self.locked_out = False
        # Clear password field
        self.password_field.clear()
        # Hide error label
        self.error_label.hide()
        # Set focus to password field
        self.password_field.setFocus()
        # Reset last activity time
        self.last_activity_time = QtCore.QDateTime.currentDateTime()

    def closeEvent(self, event):
        """Called when the lock screen is closed."""
        # Stop all timers
        if hasattr(self, 'clock_timer'):
            self.clock_timer.stop()
        if hasattr(self, 'inactivity_timer'):
            self.inactivity_timer.stop()
        if hasattr(self, 'slideshow_timer'):
            self.slideshow_timer.stop()
        if hasattr(self, 'lockout_timer') and self.lockout_timer:
            self.lockout_timer.stop()
        super().closeEvent(event)

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
