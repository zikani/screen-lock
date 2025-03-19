from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox,
    QSpinBox, QComboBox, QGroupBox, QFormLayout, QTabWidget, QFileDialog, QColorDialog, 
    QMessageBox, QSlider, QProgressBar, QRadioButton, QButtonGroup, QToolTip, QApplication
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QPalette, QIcon, QFont, QPixmap

from utils import is_windows

class SettingsPanelUI:
    def setupUI(self, dialog):
        # Apply dark theme with improved colors
        dark_stylesheet = """
            QWidget {
                background-color: #1E1E1E;
                color: #FFFFFF;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLineEdit, QSpinBox, QComboBox, QSlider {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #3D3D3D;
                border-radius: 4px;
                padding: 4px;
                selection-background-color: #3D7EFF;
            }
            QPushButton {
                background-color: #3D7EFF;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5C8FFF;
            }
            QPushButton:pressed {
                background-color: #2D6EFF;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QCheckBox {
                color: #FFFFFF;
                spacing: 6px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QRadioButton {
                color: #FFFFFF;
                spacing: 6px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
            QGroupBox {
                color: #FFFFFF;
                border: 1px solid #3D3D3D;
                border-radius: 4px;
                margin-top: 12px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 5px;
            }
            QTabWidget::pane {
                border: 1px solid #3D3D3D;
                border-radius: 4px;
            }
            QTabBar::tab {
                background: #2D2D2D;
                color: #FFFFFF;
                padding: 8px 12px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #3D7EFF;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected {
                background: #3D3D3D;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #2D2D2D;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #3D7EFF;
                width: 16px;
                margin: -4px 0;
                border-radius: 8px;
            }
            QSlider::add-page:horizontal {
                background: #2D2D2D;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #3D7EFF;
                border-radius: 3px;
            }
            QProgressBar {
                border: 1px solid #3D3D3D;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3D7EFF;
                width: 8px;
            }
            QLabel {
                color: #FFFFFF;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 12px;
                border-left-width: 1px;
                border-left-color: #3D3D3D;
                border-left-style: solid;
            }
            QToolTip {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #3D3D3D;
                border-radius: 4px;
                padding: 4px;
            }
        """
        dialog.setStyleSheet(dark_stylesheet)

        # Set window properties
        dialog.setWindowTitle("Screen Locker Settings")
        dialog.setFixedSize(570, 700)
        

        # Main layout
        self.main_layout = QVBoxLayout(dialog)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(8)

        # Create tabs
        self.tabs = QTabWidget()

        # General settings tab
        self.general_tab = QWidget()
        self.general_layout = QVBoxLayout(self.general_tab)
        self.general_layout.setContentsMargins(8, 8, 8, 8)
        self.general_layout.setSpacing(8)

        # Hotkey settings
        self.hotkey_group = QGroupBox("Hotkey Settings")
        self.hotkey_layout = QFormLayout()
        self.hotkey_layout.setVerticalSpacing(6)
        self.hotkey_layout.setLabelAlignment(Qt.AlignRight)

        self.hotkey_edit = QLineEdit()
        self.hotkey_edit.setPlaceholderText("Press keys...")
        self.hotkey_edit.setReadOnly(True)
        self.hotkey_edit.setToolTip("🛠️ Press a key combination (e.g., Ctrl+Alt+L) to set the hotkey.")
        self.hotkey_layout.addRow("Lock Screen Hotkey:", self.hotkey_edit)

        self.clear_hotkey_btn = QPushButton("Clear Hotkey")
        self.clear_hotkey_btn.setToolTip("🧹 Clear the current hotkey.")
        self.hotkey_layout.addRow("", self.clear_hotkey_btn)
        self.hotkey_group.setLayout(self.hotkey_layout)

        # Timer settings
        self.timer_group = QGroupBox("Automatic Lock")
        self.timer_layout = QFormLayout()
        self.timer_layout.setVerticalSpacing(6)
        self.timer_layout.setLabelAlignment(Qt.AlignRight)

        self.enable_timer = QCheckBox("Enable auto-lock")
        self.enable_timer.setToolTip("🕒 Enable automatic locking after inactivity.")
        self.idle_timer = QSpinBox()
        self.idle_timer.setRange(1, 180)  # Extended range to 3 hours
        self.idle_timer.setValue(5)
        self.idle_timer.setSuffix(" minutes")
        self.idle_timer.setToolTip("⏳ Set the idle timeout in minutes (1–180).")

        self.timer_layout.addRow("", self.enable_timer)
        self.timer_layout.addRow("Lock after inactivity:", self.idle_timer)

        self.idle_slider = QSlider(Qt.Horizontal)
        self.idle_slider.setRange(1, 180)
        self.idle_slider.setValue(5)
        self.idle_slider.setToolTip("⏳ Slide to adjust the idle timeout.")
        self.timer_layout.addRow("", self.idle_slider)

        self.timer_group.setLayout(self.timer_layout)

        # Password settings
        self.password_group = QGroupBox("Password Protection")
        self.password_layout = QFormLayout()
        self.password_layout.setVerticalSpacing(6)
        self.password_layout.setLabelAlignment(Qt.AlignRight)

        self.enable_password = QCheckBox("Enable password")
        self.enable_password.setToolTip("🔒 Enable password protection.")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Enter password")
        self.password_edit.setToolTip("🔑 Enter a password to unlock the screen.")

        self.show_password = QCheckBox("Show password")
        self.show_password.setToolTip("👁️ Show or hide the password text.")

        self.password_confirm = QLineEdit()
        self.password_confirm.setEchoMode(QLineEdit.Password)
        self.password_confirm.setPlaceholderText("Confirm password")
        self.password_confirm.setToolTip("🔑 Confirm your password.")

        self.password_strength = QProgressBar()
        self.password_strength.setRange(0, 100)
        self.password_strength.setValue(0)
        self.password_strength.setToolTip("🔒 Password strength indicator.")

        self.password_layout.addRow("", self.enable_password)
        self.password_layout.addRow("Password:", self.password_edit)
        self.password_layout.addRow("", self.show_password)
        self.password_layout.addRow("Confirm Password:", self.password_confirm)
        self.password_layout.addRow("Password Strength:", self.password_strength)
        self.password_group.setLayout(self.password_layout)

        # Behavior settings
        self.behavior_group = QGroupBox("Behavior Settings")
        self.behavior_layout = QFormLayout()
        self.behavior_layout.setVerticalSpacing(6)

        # Hot Corners
        self.hot_corners_checkbox = QCheckBox("Enable Hot Corners")
        self.hot_corners_checkbox.setToolTip("🖱️ Enable hot corners to lock the screen.")
        self.hot_corners_combo = QComboBox()
        self.hot_corners_combo.addItems(["Top Left", "Top Right", "Bottom Left", "Bottom Right"])
        self.hot_corners_combo.setToolTip("🖱️ Choose the corner that triggers the lock.")

        self.behavior_layout.addRow("", self.hot_corners_checkbox)
        self.behavior_layout.addRow("Active Corner:", self.hot_corners_combo)

        # Lock on Startup/Sleep
        self.lock_on_startup_checkbox = QCheckBox("Lock on Startup")
        self.lock_on_startup_checkbox.setToolTip("🔒 Lock the screen when the application starts.")
        self.lock_on_sleep_checkbox = QCheckBox("Lock on Sleep")
        self.lock_on_sleep_checkbox.setToolTip("💤 Lock the screen when the system goes to sleep.")
        self.lock_on_screensaver_checkbox = QCheckBox("Lock on Screensaver")
        self.lock_on_screensaver_checkbox.setToolTip("🖼️ Lock the screen when the screensaver activates.")

        self.behavior_layout.addRow("", self.lock_on_startup_checkbox)
        self.behavior_layout.addRow("", self.lock_on_sleep_checkbox)
        self.behavior_layout.addRow("", self.lock_on_screensaver_checkbox)

        # Autostart
        self.autostart_checkbox = QCheckBox("Enable Autostart")
        self.autostart_checkbox.setToolTip("🚀 Start the application automatically on system login.")
        self.behavior_layout.addRow("", self.autostart_checkbox)

        self.behavior_group.setLayout(self.behavior_layout)

        # Add groups to general tab
        self.general_layout.addWidget(self.hotkey_group)
        self.general_layout.addWidget(self.timer_group)
        self.general_layout.addWidget(self.password_group)
        self.general_layout.addWidget(self.behavior_group)

        # Windows Integration settings
        if is_windows():
            self.windows_group = QGroupBox("Windows Integration")
            self.windows_layout = QFormLayout()
            self.windows_layout.setVerticalSpacing(6)

            self.set_default_lock = QCheckBox("Set as default Windows lock screen")
            self.set_default_lock.setToolTip("🔒 Replace the default Windows lock screen (requires admin)")
            
            self.replace_win_l = QCheckBox("Replace Win+L shortcut")
            self.replace_win_l.setToolTip("⌨️ Handle the Windows+L keyboard shortcut")
            
            self.secure_desktop = QCheckBox("Use secure desktop")
            self.secure_desktop.setToolTip("🛡️ Run on Windows secure desktop for enhanced security")
            
            self.windows_layout.addRow("", self.set_default_lock)
            self.windows_layout.addRow("", self.replace_win_l)
            self.windows_layout.addRow("", self.secure_desktop)
            
            self.windows_group.setLayout(self.windows_layout)
            self.general_layout.addWidget(self.windows_group)

        self.general_layout.addStretch()

        # Appearance settings tab
        self.appearance_tab = QWidget()
        self.appearance_layout = QVBoxLayout(self.appearance_tab)
        self.appearance_layout.setContentsMargins(8, 8, 8, 8)
        self.appearance_layout.setSpacing(8)

        # Background settings
        self.bg_group = QGroupBox("Background")
        self.bg_layout = QFormLayout()
        self.bg_layout.setVerticalSpacing(6)
        self.bg_layout.setLabelAlignment(Qt.AlignRight)

        self.bg_type = QComboBox()
        self.bg_type.addItems(["Solid Color", "Image", "Slideshow", "Blur Current Desktop"])
        self.bg_type.setToolTip("🎨 Choose the background type.")
        self.bg_layout.addRow("Background Type:", self.bg_type)

        self.bg_color_btn = QPushButton("Choose Color")
        self.bg_color_btn.setToolTip("🎨 Choose a background color.")
        self.bg_color_preview = QLabel()
        self.bg_color_preview.setFixedSize(20, 20)
        self.bg_color_preview.setStyleSheet("background-color: #000000; border: 1px solid #3D3D3D; border-radius: 2px;")
        self.bg_color_layout = QHBoxLayout()
        self.bg_color_layout.addWidget(self.bg_color_btn)
        self.bg_color_layout.addWidget(self.bg_color_preview)
        self.bg_color_layout.addStretch()
        self.bg_layout.addRow("Background Color:", self.bg_color_layout)

        self.bg_image_path = QLineEdit()
        self.bg_image_path.setPlaceholderText("No image selected")
        self.bg_image_path.setReadOnly(True)
        self.bg_layout.addRow("Background Image:", self.bg_image_path)

        self.bg_image_btn = QPushButton("Browse...")
        self.bg_image_btn.setToolTip("🖼️ Select a background image.")
        self.bg_layout.addRow("", self.bg_image_btn)

        self.bg_blur_slider = QSlider(Qt.Horizontal)
        self.bg_blur_slider.setRange(0, 20)
        self.bg_blur_slider.setValue(5)
        self.bg_blur_slider.setToolTip("🌫️ Adjust the background blur amount.")
        self.bg_layout.addRow("Blur Amount:", self.bg_blur_slider)

        self.bg_opacity_slider = QSlider(Qt.Horizontal)
        self.bg_opacity_slider.setRange(0, 100)
        self.bg_opacity_slider.setValue(100)
        self.bg_opacity_slider.setToolTip("🔍 Adjust the background opacity.")
        self.bg_layout.addRow("Opacity:", self.bg_opacity_slider)

        self.bg_group.setLayout(self.bg_layout)

        # Clock settings
        self.clock_group = QGroupBox("Clock")
        self.clock_layout = QFormLayout()
        self.clock_layout.setVerticalSpacing(6)
        self.clock_layout.setLabelAlignment(Qt.AlignRight)

        self.enable_clock = QCheckBox("Show clock")
        self.enable_clock.setChecked(True)
        self.enable_clock.setToolTip("🕰️ Enable the clock display on the lock screen.")
        
        self.clock_format = QComboBox()
        self.clock_format.addItems(["12 Hour", "24 Hour"])
        self.clock_format.setToolTip("⏲️ Choose the clock format.")
        
        self.clock_size = QSpinBox()
        self.clock_size.setRange(10, 200)
        self.clock_size.setValue(40)
        self.clock_size.setSuffix(" pt")
        self.clock_size.setToolTip("🔠 Set the clock font size.")
        
        self.clock_color_btn = QPushButton("Choose Color")
        self.clock_color_btn.setToolTip("🎨 Choose the clock text color.")
        
        self.clock_color_preview = QLabel()
        self.clock_color_preview.setFixedSize(20, 20)
        self.clock_color_preview.setStyleSheet("background-color: #FFFFFF; border: 1px solid #3D3D3D; border-radius: 2px;")
        self.clock_color_layout = QHBoxLayout()
        self.clock_color_layout.addWidget(self.clock_color_btn)
        self.clock_color_layout.addWidget(self.clock_color_preview)
        self.clock_color_layout.addStretch()

        self.show_date = QCheckBox("Show date")
        self.show_date.setChecked(True)
        self.show_date.setToolTip("📅 Show the current date on the lock screen.")
        
        self.date_format = QComboBox()
        self.date_format.addItems(["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD"])
        self.date_format.setToolTip("📅 Choose the date format.")

        self.clock_font = QComboBox()
        self.clock_font.addItems(["System Default", "Arial", "Times New Roman", "Courier New", "Verdana"])
        self.clock_font.setToolTip("🔤 Choose the clock font.")

        self.clock_layout.addRow("", self.enable_clock)
        self.clock_layout.addRow("Format:", self.clock_format)
        self.clock_layout.addRow("Font:", self.clock_font)
        self.clock_layout.addRow("Font Size:", self.clock_size)
        self.clock_layout.addRow("Font Color:", self.clock_color_layout)
        self.clock_layout.addRow("", self.show_date)
        self.clock_layout.addRow("Date Format:", self.date_format)
        self.clock_group.setLayout(self.clock_layout)

        # UI Elements
        self.ui_group = QGroupBox("UI Elements")
        self.ui_layout = QFormLayout()
        self.ui_layout.setVerticalSpacing(6)

        self.show_unlock_button = QCheckBox("Show unlock button")
        self.show_unlock_button.setChecked(True)
        self.show_unlock_button.setToolTip("🔓 Show a button to unlock the screen.")

        self.show_user_avatar = QCheckBox("Show user avatar")
        self.show_user_avatar.setChecked(True)
        self.show_user_avatar.setToolTip("👤 Show the user's avatar on the lock screen.")

        self.show_keyboard_layout = QCheckBox("Show keyboard layout")
        self.show_keyboard_layout.setChecked(False)
        self.show_keyboard_layout.setToolTip("⌨️ Show the current keyboard layout on the lock screen.")

        self.ui_layout.addRow("", self.show_unlock_button)
        self.ui_layout.addRow("", self.show_user_avatar)
        self.ui_layout.addRow("", self.show_keyboard_layout)

        self.ui_group.setLayout(self.ui_layout)

        # Add groups to appearance tab
        self.appearance_layout.addWidget(self.bg_group)
        self.appearance_layout.addWidget(self.clock_group)
        self.appearance_layout.addWidget(self.ui_group)
        self.appearance_layout.addStretch()

        # Security settings tab
        self.security_tab = QWidget()
        self.security_layout = QVBoxLayout(self.security_tab)
        self.security_layout.setContentsMargins(8, 8, 8, 8)
        self.security_layout.setSpacing(8)

        # Webcam Detection
        self.webcam_detection_group = QGroupBox("Webcam Detection")
        self.webcam_detection_layout = QFormLayout()
        self.webcam_detection_layout.setVerticalSpacing(6)
        self.webcam_detection_layout.setLabelAlignment(Qt.AlignRight)

        self.webcam_detection_checkbox = QCheckBox("Enable Webcam Detection")
        self.webcam_detection_checkbox.setToolTip("📷 Enable webcam detection to lock the screen when no face is detected.")
        self.webcam_detection_layout.addRow("", self.webcam_detection_checkbox)

        self.webcam_sensitivity_slider = QSlider(Qt.Horizontal)
        self.webcam_sensitivity_slider.setRange(1, 10)
        self.webcam_sensitivity_slider.setValue(5)
        self.webcam_sensitivity_slider.setToolTip("📊 Adjust the sensitivity of webcam detection.")
        self.webcam_detection_layout.addRow("Webcam Sensitivity:", self.webcam_sensitivity_slider)

        self.webcam_timeout = QSpinBox()
        self.webcam_timeout.setRange(5, 60)
        self.webcam_timeout.setValue(15)
        self.webcam_timeout.setSuffix(" seconds")
        self.webcam_timeout.setToolTip("⏱️ Set how long to wait before locking when no face is detected.")
        self.webcam_detection_layout.addRow("Lock Timeout:", self.webcam_timeout)

        self.test_webcam_btn = QPushButton("Test Webcam")
        self.test_webcam_btn.setToolTip("🔍 Test the webcam detection.")
        self.webcam_detection_layout.addRow("", self.test_webcam_btn)

        self.webcam_detection_group.setLayout(self.webcam_detection_layout)
        self.security_layout.addWidget(self.webcam_detection_group)

        # Authentication Methods
        self.auth_method_group = QGroupBox("Authentication Method")
        self.auth_method_layout = QVBoxLayout()

        self.auth_method_radio_group = QButtonGroup()
        self.auth_password_radio = QRadioButton("Password")
        self.auth_pin_radio = QRadioButton("PIN")
        self.auth_pattern_radio = QRadioButton("Pattern")
        self.auth_fingerprint_radio = QRadioButton("Fingerprint")
        self.auth_face_radio = QRadioButton("Face Recognition")

        self.auth_method_radio_group.addButton(self.auth_password_radio)
        self.auth_method_radio_group.addButton(self.auth_pin_radio)
        self.auth_method_radio_group.addButton(self.auth_pattern_radio)
        self.auth_method_radio_group.addButton(self.auth_fingerprint_radio)
        self.auth_method_radio_group.addButton(self.auth_face_radio)

        self.auth_password_radio.setChecked(True)
        
        self.auth_method_layout.addWidget(self.auth_password_radio)
        self.auth_method_layout.addWidget(self.auth_pin_radio)
        self.auth_method_layout.addWidget(self.auth_pattern_radio)
        self.auth_method_layout.addWidget(self.auth_fingerprint_radio)
        self.auth_method_layout.addWidget(self.auth_face_radio)

        self.configure_auth_btn = QPushButton("Configure Selected Method")
        self.configure_auth_btn.setToolTip("🔧 Configure the selected authentication method.")
        self.auth_method_layout.addWidget(self.configure_auth_btn)

        self.auth_method_group.setLayout(self.auth_method_layout)
        self.security_layout.addWidget(self.auth_method_group)

        # Two-Factor Authentication
        self.two_factor_group = QGroupBox("Two-Factor Authentication")
        self.two_factor_layout = QFormLayout()
        self.two_factor_layout.setVerticalSpacing(6)
        self.two_factor_layout.setLabelAlignment(Qt.AlignRight)

        self.two_factor_checkbox = QCheckBox("Enable Two-Factor Authentication")
        self.two_factor_checkbox.setToolTip("🔐 Add an extra layer of security with 2FA.")
        self.two_factor_layout.addRow("", self.two_factor_checkbox)

        self.two_factor_method_combo = QComboBox()
        self.two_factor_method_combo.addItems(["Email", "SMS", "Authenticator App"])
        self.two_factor_method_combo.setToolTip("📧 Choose the 2FA method.")
        self.two_factor_layout.addRow("Method:", self.two_factor_method_combo)

        self.two_factor_email = QLineEdit()
        self.two_factor_email.setPlaceholderText("Enter email address")
        self.two_factor_email.setToolTip("📧 Enter your email address for 2FA.")
        self.two_factor_layout.addRow("Email:", self.two_factor_email)

        self.two_factor_test_btn = QPushButton("Test 2FA")
        self.two_factor_test_btn.setToolTip("🔍 Test the two-factor authentication setup.")
        self.two_factor_layout.addRow("", self.two_factor_test_btn)

        self.two_factor_group.setLayout(self.two_factor_layout)
        self.security_layout.addWidget(self.two_factor_group)

        # Security Options
        self.security_options_group = QGroupBox("Additional Security Options")
        self.security_options_layout = QFormLayout()
        self.security_options_layout.setVerticalSpacing(6)

        self.failed_attempts_spinbox = QSpinBox()
        self.failed_attempts_spinbox.setRange(3, 10)
        self.failed_attempts_spinbox.setValue(5)
        self.failed_attempts_spinbox.setToolTip("🔒 Maximum number of failed unlock attempts before lockout.")
        self.security_options_layout.addRow("Max Failed Attempts:", self.failed_attempts_spinbox)

        self.lockout_duration_spinbox = QSpinBox()
        self.lockout_duration_spinbox.setRange(1, 60)
        self.lockout_duration_spinbox.setValue(5)
        self.lockout_duration_spinbox.setSuffix(" minutes")
        self.lockout_duration_spinbox.setToolTip("⏳ Duration of lockout after max failed attempts.")
        self.security_options_layout.addRow("Lockout Duration:", self.lockout_duration_spinbox)

        self.password_expiry_checkbox = QCheckBox("Enable password expiry")
        self.password_expiry_checkbox.setToolTip("🕒 Force password change after a set period.")
        self.security_options_layout.addRow("", self.password_expiry_checkbox)

        self.password_expiry_spinbox = QSpinBox()
        self.password_expiry_spinbox.setRange(1, 365)
        self.password_expiry_spinbox.setValue(90)
        self.password_expiry_spinbox.setSuffix(" days")
        self.password_expiry_spinbox.setToolTip("📅 Number of days before password expires.")
        self.security_options_layout.addRow("Password Expiry:", self.password_expiry_spinbox)

        self.security_options_group.setLayout(self.security_options_layout)
        self.security_layout.addWidget(self.security_options_group)

        # Advanced settings
        self.advanced_group = QGroupBox("Advanced Settings")
        self.advanced_layout = QFormLayout()
        self.advanced_layout.setVerticalSpacing(6)

        self.debug_mode = QCheckBox("Enable debug mode")
        self.debug_mode.setToolTip("🐛 Enable debug mode for testing.")
        self.advanced_layout.addRow("", self.debug_mode)

        self.console_output = QCheckBox("Show console output")
        self.console_output.setToolTip("💻 Show console with debug information.")
        self.advanced_layout.addRow("", self.console_output)

        self.export_settings_btn = QPushButton("Export Settings")
        self.export_settings_btn.setToolTip("📤 Export settings to a file.")
        self.advanced_layout.addRow("", self.export_settings_btn)

        self.import_settings_btn = QPushButton("Import Settings")
        self.import_settings_btn.setToolTip("📥 Import settings from a file.")
        self.advanced_layout.addRow("", self.import_settings_btn)

        self.advanced_group.setLayout(self.advanced_layout)
        self.security_layout.addWidget(self.advanced_group)

        self.security_layout.addStretch()

        # About tab
        self.about_tab = QWidget()
        self.about_layout = QVBoxLayout(self.about_tab)
        self.about_layout.setContentsMargins(8, 8, 8, 8)
        self.about_layout.setSpacing(8)

        # App info
        self.about_group = QGroupBox("About Screen Locker")
        self.about_layout_inner = QVBoxLayout()

        self.app_logo_label = QLabel()
        # Set a placeholder for the app logo
        self.app_logo_label.setFixedSize(96, 96)
        self.app_logo_label.setAlignment(Qt.AlignCenter)
        self.app_logo_label.setStyleSheet("background-color: #3D7EFF; border-radius: 12px;")
        self.about_layout_inner.addWidget(self.app_logo_label, 0, Qt.AlignCenter)

        self.app_name_label = QLabel("Screen Locker")
        self.app_name_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.app_name_label.setFont(font)
        self.about_layout_inner.addWidget(self.app_name_label, 0, Qt.AlignCenter)

        self.app_version_label = QLabel("Version 1.2.0")
        self.app_version_label.setAlignment(Qt.AlignCenter)
        self.about_layout_inner.addWidget(self.app_version_label, 0, Qt.AlignCenter)

        self.about_label = QLabel(
            "A secure and customizable application to lock your screen with advanced features.\n\n"
            "Key Features:\n"
            "• Hotkey locking\n"
            "• Multiple authentication methods\n"
            "• Two-factor authentication\n"
            "• Webcam detection\n"
            "• Customizable appearance\n"
            "• Automatic locking\n"
            "• Hot corners detection\n"
            "• Secure password handling\n\n"
            "© 2025 All rights reserved."
        )
        self.about_label.setAlignment(Qt.AlignLeft)
        self.about_label.setWordWrap(True)
        self.about_layout_inner.addWidget(self.about_label)

        self.about_group.setLayout(self.about_layout_inner)
        self.about_layout.addWidget(self.about_group)

        # Developer info
        self.developer_group = QGroupBox("Developer Information")
        self.developer_layout = QVBoxLayout()

        self.developer_label = QLabel(
            "Developed by: Your Name\n"
            "Email: contact@example.com\n"
            "Website: www.example.com"
        )
        self.developer_label.setWordWrap(True)
        self.developer_layout.addWidget(self.developer_label)

        self.report_bug_btn = QPushButton("Report a Bug")
        self.report_bug_btn.setToolTip("🐛 Report a bug or issue.")
        self.developer_layout.addWidget(self.report_bug_btn)

        self.check_updates_btn = QPushButton("Check for Updates")
        self.check_updates_btn.setToolTip("🔄 Check for software updates.")
        self.developer_layout.addWidget(self.check_updates_btn)

        self.developer_group.setLayout(self.developer_layout)
        self.about_layout.addWidget(self.developer_group)

        # License info
        self.license_group = QGroupBox("License Information")
        self.license_layout = QVBoxLayout()

        self.license_label = QLabel(
            "This software is released under the MIT License.\n\n"
            "Permission is hereby granted, free of charge, to any person obtaining a copy "
            "of this software and associated documentation files (the \"Software\"), to deal "
            "in the Software without restriction, including without limitation the rights "
            "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell "
            "copies of the Software, and to permit persons to whom the Software is "
            "furnished to do so, subject to the following conditions:\n\n"
            "The above copyright notice and this permission notice shall be included in all "
            "copies or substantial portions of the Software."
        )
        self.license_label.setWordWrap(True)
        self.license_layout.addWidget(self.license_label)

        self.license_group.setLayout(self.license_layout)
        self.about_layout.addWidget(self.license_group)

        self.about_layout.addStretch()

        # Add all tabs to the tab widget
        self.tabs.addTab(self.general_tab, "General")
        self.tabs.addTab(self.appearance_tab, "Appearance")
        self.tabs.addTab(self.security_tab, "Security")
        self.tabs.addTab(self.about_tab, "About")

        # Add tabs to main layout
        self.main_layout.addWidget(self.tabs)

        # Add buttons at the bottom
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setSpacing(6)

        self.restore_defaults_btn = QPushButton("Restore Defaults")
        self.restore_defaults_btn.setToolTip("↩️ Restore all settings to default values.")
        self.buttons_layout.addWidget(self.restore_defaults_btn)

        self.buttons_layout.addStretch()

        self.apply_btn = QPushButton("Apply")
        self.apply_btn.setToolTip("✅ Apply changes without closing the window.")
        self.buttons_layout.addWidget(self.apply_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setToolTip("❌ Cancel changes and close the window.")
        self.buttons_layout.addWidget(self.cancel_btn)

        self.ok_btn = QPushButton("OK")
        self.ok_btn.setToolTip("✅ Save changes and close the window.")
        self.buttons_layout.addWidget(self.ok_btn)

        self.main_layout.addLayout(self.buttons_layout)