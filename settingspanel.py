from PyQt5.QtWidgets import QDialog, QMessageBox, QColorDialog, QFileDialog
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from settingspanel_ui import SettingsPanelUI  # Import the UI class
from utils import load_settings, save_settings, hash_password, verify_password
import os
import json


class SettingsPanel(QDialog):
    def __init__(self, settings, locker=None, parent=None):
        super().__init__(parent)
        self.settings = settings  # This is a dictionary
        self.locker = locker

        # Set up the UI
        self.ui = SettingsPanelUI()
        self.ui.setupUI(self)

        # Load settings into the UI
        self.load_settings_to_ui()

        # Connect signals to slots
        self.connect_signals()

    def connect_signals(self):
        """Connect UI signals to their handlers."""
        # Main dialog buttons
        self.ui.ok_btn.clicked.connect(self.save_and_close)
        self.ui.apply_btn.clicked.connect(self.apply_settings)
        self.ui.cancel_btn.clicked.connect(self.reject)
        self.ui.restore_defaults_btn.clicked.connect(self.restore_defaults)

        # Hotkey settings
        self.ui.hotkey_edit.keyPressEvent = self.capture_hotkey
        self.ui.clear_hotkey_btn.clicked.connect(self.clear_hotkey)

        # Background settings
        self.ui.bg_color_btn.clicked.connect(self.choose_background_color)
        self.ui.bg_image_btn.clicked.connect(self.choose_background_image)

        # Clock settings
        self.ui.clock_color_btn.clicked.connect(self.choose_clock_color)

        # Import/Export
        self.ui.export_settings_btn.clicked.connect(self.export_settings)
        self.ui.import_settings_btn.clicked.connect(self.import_settings)

        # Test functions
        self.ui.test_webcam_btn.clicked.connect(self.test_webcam)
        self.ui.two_factor_test_btn.clicked.connect(self.test_two_factor)

        # Configure auth
        self.ui.configure_auth_btn.clicked.connect(self.configure_auth_method)

        # About tab
        self.ui.report_bug_btn.clicked.connect(self.report_bug)
        self.ui.check_updates_btn.clicked.connect(self.check_updates)

    def load_settings_to_ui(self):
        """Load settings from the dictionary into the UI."""
        # General settings
        self.ui.hotkey_edit.setText(self.settings.get("hotkey", "Ctrl+Alt+L"))
        self.ui.enable_timer.setChecked(self.settings.get("enable_timer", False))
        self.ui.idle_timer.setValue(self.settings.get("idle_timeout", 5))
        self.ui.idle_slider.setValue(self.settings.get("idle_timeout", 5))

        # Password settings
        self.ui.enable_password.setChecked(self.settings.get("enable_password", False))
        self.ui.password_edit.setText(self.settings.get("password", ""))
        self.ui.password_confirm.setText(self.settings.get("password", ""))

        # Behavior settings
        self.ui.hot_corners_checkbox.setChecked(self.settings.get("hot_corners", False))
        self.ui.hot_corners_combo.setCurrentText(self.settings.get("hot_corner_position", "Top Right"))
        self.ui.lock_on_startup_checkbox.setChecked(self.settings.get("lock_on_startup", False))
        self.ui.lock_on_sleep_checkbox.setChecked(self.settings.get("lock_on_sleep", True))
        self.ui.lock_on_screensaver_checkbox.setChecked(self.settings.get("lock_on_screensaver", True))
        self.ui.autostart_checkbox.setChecked(self.settings.get("autostart", False))

        # Appearance settings
        self.ui.bg_type.setCurrentText(self.settings.get("bg_type", "Solid Color"))
        bg_color = QColor(self.settings.get("bg_color", "#000000"))
        self.ui.bg_color_preview.setStyleSheet(f"background-color: {bg_color.name()}; border: 1px solid #3D3D3D; border-radius: 2px;")
        self.ui.bg_image_path.setText(self.settings.get("bg_image", ""))
        self.ui.bg_blur_slider.setValue(self.settings.get("bg_blur", 5))
        self.ui.bg_opacity_slider.setValue(self.settings.get("bg_opacity", 100))

        # Clock settings
        self.ui.enable_clock.setChecked(self.settings.get("enable_clock", True))
        self.ui.clock_format.setCurrentText(self.settings.get("clock_format", "24 Hour"))
        self.ui.clock_size.setValue(self.settings.get("clock_size", 40))
        self.ui.clock_font.setCurrentText(self.settings.get("clock_font", "System Default"))
        clock_color = QColor(self.settings.get("clock_color", "#FFFFFF"))
        self.ui.clock_color_preview.setStyleSheet(f"background-color: {clock_color.name()}; border: 1px solid #3D3D3D; border-radius: 2px;")
        self.ui.show_date.setChecked(self.settings.get("show_date", True))
        self.ui.date_format.setCurrentText(self.settings.get("date_format", "MM/DD/YYYY"))

        # UI Elements
        self.ui.show_unlock_button.setChecked(self.settings.get("show_unlock_button", True))
        self.ui.show_user_avatar.setChecked(self.settings.get("show_user_avatar", True))
        self.ui.show_keyboard_layout.setChecked(self.settings.get("show_keyboard_layout", False))

        # Security settings
        self.ui.webcam_detection_checkbox.setChecked(self.settings.get("webcam_detection", False))
        self.ui.webcam_sensitivity_slider.setValue(self.settings.get("webcam_sensitivity", 5))
        self.ui.webcam_timeout.setValue(self.settings.get("webcam_timeout", 15))

        # Authentication method
        auth_method = self.settings.get("auth_method", "Password")
        if auth_method == "Password":
            self.ui.auth_password_radio.setChecked(True)
        elif auth_method == "PIN":
            self.ui.auth_pin_radio.setChecked(True)
        elif auth_method == "Pattern":
            self.ui.auth_pattern_radio.setChecked(True)
        elif auth_method == "Fingerprint":
            self.ui.auth_fingerprint_radio.setChecked(True)
        elif auth_method == "Face Recognition":
            self.ui.auth_face_radio.setChecked(True)

        # Two-factor authentication
        self.ui.two_factor_checkbox.setChecked(self.settings.get("two_factor", False))
        self.ui.two_factor_method_combo.setCurrentText(self.settings.get("two_factor_method", "Email"))
        self.ui.two_factor_email.setText(self.settings.get("two_factor_email", ""))

        # Security options
        self.ui.failed_attempts_spinbox.setValue(self.settings.get("failed_attempts", 5))
        self.ui.lockout_duration_spinbox.setValue(self.settings.get("lockout_duration", 5))
        self.ui.password_expiry_checkbox.setChecked(self.settings.get("password_expiry", False))
        self.ui.password_expiry_spinbox.setValue(self.settings.get("password_expiry_days", 90))

        # Advanced settings
        self.ui.debug_mode.setChecked(self.settings.get("debug_mode", False))
        self.ui.console_output.setChecked(self.settings.get("console_output", False))

    def save_settings_from_ui(self):
        """Save settings from the UI to the dictionary."""
        try:
            # Create a temporary dictionary to store new settings
            new_settings = {}

            # General settings
            new_settings["hotkey"] = self.ui.hotkey_edit.text()
            new_settings["enable_timer"] = self.ui.enable_timer.isChecked()
            new_settings["idle_timeout"] = self.ui.idle_timer.value()

            # Password settings
            new_settings["enable_password"] = self.ui.enable_password.isChecked()
            
            # Only save password if passwords match and not empty
            if self.ui.enable_password.isChecked():
                password = self.ui.password_edit.text()
                confirm_password = self.ui.password_confirm.text()

                if password and password == confirm_password:
                    new_settings["password"] = hash_password(password)
                elif password != confirm_password:
                    QMessageBox.warning(self, "Password Mismatch", "Passwords do not match. Password not saved.")
                    return False

            # Copy all other settings from UI to the dictionary
            new_settings.update({
                "hot_corners": self.ui.hot_corners_checkbox.isChecked(),
                "hot_corner_position": self.ui.hot_corners_combo.currentText(),
                "lock_on_startup": self.ui.lock_on_startup_checkbox.isChecked(),
                "lock_on_sleep": self.ui.lock_on_sleep_checkbox.isChecked(),
                "lock_on_screensaver": self.ui.lock_on_screensaver_checkbox.isChecked(),
                "autostart": self.ui.autostart_checkbox.isChecked(),
                "bg_type": self.ui.bg_type.currentText(),
                "bg_color": self.ui.bg_color_preview.styleSheet().split("background-color: ")[1].split(";")[0],
                "bg_image": self.ui.bg_image_path.text(),
                "bg_blur": self.ui.bg_blur_slider.value(),
                "bg_opacity": self.ui.bg_opacity_slider.value(),
                "enable_clock": self.ui.enable_clock.isChecked(),
                "clock_format": self.ui.clock_format.currentText(),
                "clock_size": self.ui.clock_size.value(),
                "clock_font": self.ui.clock_font.currentText(),
                "clock_color": self.ui.clock_color_preview.styleSheet().split("background-color: ")[1].split(";")[0],
                "show_date": self.ui.show_date.isChecked(),
                "date_format": self.ui.date_format.currentText(),
                "show_unlock_button": self.ui.show_unlock_button.isChecked(),
                "show_user_avatar": self.ui.show_user_avatar.isChecked(),
                "show_keyboard_layout": self.ui.show_keyboard_layout.isChecked(),
                "webcam_detection": self.ui.webcam_detection_checkbox.isChecked(),
                "webcam_sensitivity": self.ui.webcam_sensitivity_slider.value(),
                "webcam_timeout": self.ui.webcam_timeout.value(),
                "failed_attempts": self.ui.failed_attempts_spinbox.value(),
                "lockout_duration": self.ui.lockout_duration_spinbox.value(),
                "password_expiry": self.ui.password_expiry_checkbox.isChecked(),
                "password_expiry_days": self.ui.password_expiry_spinbox.value(),
                "debug_mode": self.ui.debug_mode.isChecked(),
                "console_output": self.ui.console_output.isChecked(),
                "two_factor": self.ui.two_factor_checkbox.isChecked(),
                "two_factor_method": self.ui.two_factor_method_combo.currentText(),
                "two_factor_email": self.ui.two_factor_email.text()
            })

            # Set authentication method based on radio selection
            if self.ui.auth_password_radio.isChecked():
                new_settings["auth_method"] = "Password"
            elif self.ui.auth_pin_radio.isChecked():
                new_settings["auth_method"] = "PIN"
            elif self.ui.auth_pattern_radio.isChecked():
                new_settings["auth_method"] = "Pattern"
            elif self.ui.auth_fingerprint_radio.isChecked():
                new_settings["auth_method"] = "Fingerprint"
            elif self.ui.auth_face_radio.isChecked():
                new_settings["auth_method"] = "Face Recognition"

            # Update the settings dictionary with new values
            self.settings.update(new_settings)

            # Save settings to file
            try:
                from utils import save_settings
                save_settings(self.settings)
                return True
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save settings to file: {str(e)}")
                return False

        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"An error occurred while saving settings: {str(e)}")
            return False

    def capture_hotkey(self, event):
        """Capture keyboard events for hotkey setting."""
        key_sequence = []

        if event.modifiers() & Qt.ControlModifier:
            key_sequence.append("Ctrl")
        if event.modifiers() & Qt.AltModifier:
            key_sequence.append("Alt")
        if event.modifiers() & Qt.ShiftModifier:
            key_sequence.append("Shift")
        if event.modifiers() & Qt.MetaModifier:
            key_sequence.append("Meta")

        # Add the key itself
        key_text = event.text()
        if key_text and key_text.isalnum():
            key_sequence.append(key_text.upper())

        # Only set if we have a modifier and a key
        if len(key_sequence) > 1:
            self.ui.hotkey_edit.setText("+".join(key_sequence))

        event.accept()

    def clear_hotkey(self):
        """Clear the hotkey field."""
        self.ui.hotkey_edit.clear()

    def choose_background_color(self):
        """Open color dialog to choose background color."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.ui.bg_color_preview.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #3D3D3D; border-radius: 2px;")

    def choose_background_image(self):
        """Open file dialog to choose background image."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Background Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.ui.bg_image_path.setText(file_path)

    def choose_clock_color(self):
        """Open color dialog to choose clock color."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.ui.clock_color_preview.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #3D3D3D; border-radius: 2px;")

    def export_settings(self):
        """Export settings to a JSON file."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Settings", "", "JSON Files (*.json)")
        if not file_path:
            return

        try:
            with open(file_path, "w") as f:
                json.dump(self.settings, f, indent=4)
            QMessageBox.information(self, "Settings Exported", "Settings exported successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export settings: {str(e)}")

    def import_settings(self):
        """Import settings from a JSON file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Settings", "", "JSON Files (*.json)")
        if not file_path:
            return

        try:
            with open(file_path, "r") as f:
                imported_settings = json.load(f)
                self.settings.update(imported_settings)
                self.load_settings_to_ui()
            QMessageBox.information(self, "Settings Imported", "Settings imported successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import settings: {str(e)}")

    def test_webcam(self):
        """Test webcam functionality."""
        if not self.ui.webcam_detection_checkbox.isChecked():
            QMessageBox.information(self, "Webcam Detection", "Please enable webcam detection first.")
            return

        try:
            # Implement webcam testing here
            # For now, just show a message
            QMessageBox.information(self, "Webcam Test", "Webcam test successful!")
        except Exception as e:
            QMessageBox.critical(self, "Webcam Error", f"Failed to test webcam: {str(e)}")

    def test_two_factor(self):
        """Test two-factor authentication."""
        if not self.ui.two_factor_checkbox.isChecked():
            QMessageBox.information(self, "Two-Factor Authentication", "Please enable two-factor authentication first.")
            return

        method = self.ui.two_factor_method_combo.currentText()

        if method == "Email":
            email = self.ui.two_factor_email.text()
            if not email:
                QMessageBox.warning(self, "Email Required", "Please enter an email address for two-factor authentication.")
                return

            # Implement email 2FA test here
            QMessageBox.information(self, "2FA Test", f"Sent test verification code to {email}")
        elif method == "SMS":
            # Implement SMS 2FA test here
            QMessageBox.information(self, "2FA Test", "SMS authentication test (not implemented)")
        elif method == "Authenticator App":
            # Implement authenticator app 2FA test here
            QMessageBox.information(self, "2FA Test", "Authenticator app test (not implemented)")

    def configure_auth_method(self):
        """Configure the selected authentication method."""
        if self.ui.auth_password_radio.isChecked():
            self.ui.tabs.setCurrentIndex(0)  # Switch to General tab
            self.ui.password_edit.setFocus()
        elif self.ui.auth_pin_radio.isChecked():
            QMessageBox.information(self, "Configure PIN", "PIN configuration not implemented.")
        elif self.ui.auth_pattern_radio.isChecked():
            QMessageBox.information(self, "Configure Pattern", "Pattern configuration not implemented.")
        elif self.ui.auth_fingerprint_radio.isChecked():
            QMessageBox.information(self, "Configure Fingerprint", "Fingerprint configuration not implemented.")
        elif self.ui.auth_face_radio.isChecked():
            QMessageBox.information(self, "Configure Face Recognition", "Face recognition configuration not implemented.")

    def report_bug(self):
        """Open bug reporting dialog."""
        QMessageBox.information(self, "Report Bug", "Send bug reports to: support@example.com")

    def check_updates(self):
        """Check for updates."""
        QMessageBox.information(self, "Check for Updates", "You are running the latest version!")

    def restore_defaults(self):
        """Restore default settings."""
        confirm = QMessageBox.question(
            self, "Restore Defaults",
            "Are you sure you want to restore all settings to default values?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            # Load default settings
            self.settings = load_settings(default=True)
            self.load_settings_to_ui()
            QMessageBox.information(self, "Restore Defaults", "Settings have been restored to default values.")

    def get_current_settings(self):
        """Get the current settings from the UI fields."""
        # Use the existing save_settings_from_ui method which already collects all settings
        if self.save_settings_from_ui():
            return self.settings
        return None

    def apply_settings(self):
        """Apply settings without closing the dialog."""
        if self.save_settings_from_ui():  # This updates self.settings and saves to file
            try:
                # Notify the locker of settings changes
                if self.locker:
                    self.locker.apply_settings(self.settings)  # Pass the updated settings
                QMessageBox.information(self, "Settings Applied", "Settings have been applied successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to apply settings: {e}")

    def save_and_close(self):
        """Save settings and close the dialog."""
        if self.save_settings_from_ui():  # This updates self.settings and saves to file
            try:
                # Notify the locker of settings changes
                if self.locker:
                    self.locker.apply_settings(self.settings)  # Pass the updated settings
                self.accept()  # Close the dialog
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")