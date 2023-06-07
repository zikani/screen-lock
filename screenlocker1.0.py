import os
import sys
import getpass
import csv
import logging
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QDialog,
    QSizePolicy,
    QDesktopWidget,
    QFileDialog,
    QInputDialog,
    QLineEdit,
    QCheckBox,
    QComboBox,
    QMessageBox,
    QSlider,QHBoxLayout
)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter,  QColor, QLinearGradient
from PyQt5.QtCore import Qt, pyqtSignal, QSettings,QTimer



__version__ = "1.0.0"


class BackgroundWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.background_image = QPixmap("path/to/background/image")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.drawPixmap(self.rect(), self.background_image)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Screen Lock')
        self.setFixedSize(470, 470)
        self.setWindowIcon(QIcon('path/to/lock_icon.png'))
        self.center_window()

        pc_username = getpass.getuser()

       
        font = QFont('Arial', 16, QFont.Bold)

        style_sheet = 'color: #ffffff; background-color: #0088cc; padding: 10px; border-radius: 5px;'

        hello_label = QLabel("Hello")
        hello_label.setAlignment(Qt.AlignCenter)
        hello_label.setFont(font)
        hello_label.setStyleSheet(style_sheet)

        username_label = QLabel(pc_username)
        username_label.setAlignment(Qt.AlignCenter)
        username_label.setFont(font)
        username_label.setStyleSheet(style_sheet)

        welcome_label = QLabel("Welcome to Screen Lock App")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setFont(font)
        welcome_label.setStyleSheet(style_sheet)

        settings_button = QPushButton('Settings')
        settings_button.clicked.connect(self.open_settings)
        settings_button.setFixedHeight(70)
        settings_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        settings_button.setStyleSheet('font-size: 20px;')
        settings_button.setStyleSheet('QPushButton:pressed { background-color: #990000; }')

        lock_button = QPushButton('Lock Screen')
        lock_button.clicked.connect(self.lock_screen)
        lock_button.setFixedHeight(70)
        lock_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lock_button.setStyleSheet('font-size: 40px; background-color: #FF0000;')
        lock_button.setStyleSheet('QPushButton:hover { background-color: #FF6666; }')
        lock_button.setStyleSheet('QPushButton:pressed { background-color: #990000; }')

        layout = QVBoxLayout()
        layout.addWidget(hello_label)
        layout.addWidget(username_label)
        layout.addWidget(welcome_label)
        layout.addWidget(settings_button)
        layout.addWidget(lock_button)
        layout.addStretch()

        version_label = QLabel(f"Version: {__version__}")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)

        main_widget = QWidget()
        main_widget.setLayout(layout)

        self.user_credentials = None

        background_widget = BackgroundWidget()
        background_layout = QVBoxLayout()
        background_layout.addWidget(background_widget)
        background_layout.addWidget(main_widget)

        self.setLayout(background_layout)

    def lock_screen(self):
        self.user_credentials = self.load_user_credentials()

        lock_dialog = LockDialog()
        lock_dialog.exec_()

    def load_user_credentials(self):
        settings_dialog = SettingsDialog(self)  # Assuming you have a SettingsDialog class
        return settings_dialog.load_user_credentials()

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#0088cc"))
        gradient.setColorAt(1, QColor("#004466"))
        painter.fillRect(self.rect(), gradient)

    def center_window(self):
        frame = self.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(center)
        self.move(frame.topLeft())

    def open_settings(self):
        settings_dialog = SettingsDialog(self)
        settings_dialog.background_image_selected.connect(self.set_background_image)
        settings_dialog.exec_()

    def set_background_image(self, pixmap):
        # Set the background image in the BackgroundWidget
        background_widget = self.findChild(BackgroundWidget)
        background_widget.background_image = pixmap
        background_widget.update()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape or key == Qt.Key_Q:
            self.close()







#--------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------

class SettingsDialog(QDialog):
    background_image_selected = pyqtSignal(QPixmap, bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Settings')
        self.setFixedSize(670, 670)

        
        # Initialize the logger
        self.settings_logger = logging.getLogger('settings_logger')
        self.settings_logger.setLevel(logging.ERROR)

        # Create a file handler and set its level to ERROR
        file_handler = logging.FileHandler('settings.log')
        file_handler.setLevel(logging.ERROR)

        # Create a formatter and add it to the file handler
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # Add the file handler to the logger
        self.settings_logger.addHandler(file_handler)
        self.background_folder_lineEdit = None
        self.background_image_lineEdit = None
        self.preview_label = None
        self.user_credentials = self.load_user_credentials()
        self.settings = QSettings("MyApp", "ScreenLocker")
        self.auto_timer_checkbox = None

        self.init_ui()
        self.setup_auto_timer()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout()

        
        theme_label = QLabel('Select Theme:')
        theme_dropdown = QComboBox()
        theme_dropdown.addItems(['Default', 'Dark', 'Light'])
        theme_dropdown.currentTextChanged.connect(self.apply_theme)
        layout.addWidget(theme_label)
        layout.addWidget(theme_dropdown)

        self.setLayout(layout)

        create_credentials_button = QPushButton('Create User Credentials')
        create_credentials_button.clicked.connect(self.create_credentials)
        create_credentials_button.setFixedSize(200, 30)
        create_credentials_button.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #e5e5e5;
            }
            QPushButton:pressed {
                background-color: #d5d5d5;
            }
        """)
        layout.addWidget(create_credentials_button)

        change_password_button = QPushButton('Change Password')
        change_password_button.clicked.connect(self.change_password)
        change_password_button.setFixedSize(200, 30)
        change_password_button.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #e5e5e5;
            }
            QPushButton:pressed {
                background-color: #d5d5d5;
            }
        """)
        layout.addWidget(change_password_button)

        background_button = QPushButton('Choose Background')
        background_button.setFixedSize(200, 30)
        background_button.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #e5e5e5;
            }
            QPushButton:pressed {
                background-color: #d5d5d5;
            }
        """)
        background_button.clicked.connect(self.choose_background)
        layout.addWidget(background_button)

        self.preview_label = QLabel()
        self.preview_label.setFixedSize(400, 400)
        layout.addWidget(self.preview_label)

        self.auto_timer_checkbox = QCheckBox('Auto Timer')
        self.auto_timer_checkbox.setChecked(True)
        self.auto_timer_checkbox.stateChanged.connect(self.update_auto_timer)
        layout.addWidget(self.auto_timer_checkbox)

        slider_layout = QHBoxLayout()
        self.slide_time_label = QLabel('Slide Time: 0 hours')
        slider_layout.addWidget(self.slide_time_label)

        self.slide_time_slider = QSlider(Qt.Horizontal)
        self.slide_time_slider.setRange(5, 60)
        self.slide_time_slider.setTickPosition(QSlider.TicksBelow)
        self.slide_time_slider.setTickInterval(5)
        self.slide_time_slider.valueChanged.connect(self.update_slide_time_label)
        slider_layout.addWidget(self.slide_time_slider)

        layout.addLayout(slider_layout)
        self.setLayout(layout)
        
        save_button = QPushButton('Save')
        save_button.setFixedSize(200, 30)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #e5e5e5;
            }
            QPushButton:pressed {
                background-color: #d5d5d5;
            }
        """)
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)
        
        
        
        
    def apply_theme(self, theme_name):
        app= QApplication.instance()
        if theme_name == 'Default':
            # Apply default stylesheet
            app.setStyleSheet('')
        elif theme_name == 'Dark':
            # Apply dark theme stylesheet
            app.setStyleSheet('''
                /* Dark theme stylesheet rules */
                QDialog {
                    background-color: #333333;
                    color: #ffffff;
                }

                QLabel {
                    color: #ffffff;
                }

                QPushButton {
                    background-color: #555555;
                    color: #ffffff;
                    border: 1px solid #ffffff;
                    border-radius: 5px;
                    padding: 5px;
                }

                QPushButton:hover {
                    background-color: #666666;
                }

                QPushButton:pressed {
                    background-color: #444444;
                }

                QCheckBox {
                    color: #ffffff;
                }

                QSlider::groove:horizontal {
                    background-color: #666666;
                    height: 10px;
                }

                QSlider::handle:horizontal {
                    background-color: #ffffff;
                    width: 10px;
                    margin: -5px;
                }
            ''')
        elif theme_name == 'Light':
            # Apply light theme stylesheet
            app.setStyleSheet('''
                /* Light theme stylesheet rules */
                QDialog {
                    background-color: #f5f5f5;
                    color: #000000;
                }

                QLabel {
                    color: #000000;
                }

                QPushButton {
                    background-color: #e5e5e5;
                    color: #000000;
                    border: 1px solid #000000;
                    border-radius: 5px;
                    padding: 5px;
                }

                QPushButton:hover {
                    background-color: #d5d5d5;
                }

                QPushButton:pressed {
                    background-color: #f0f0f0;
                }

                QCheckBox {
                    color: #000000;
                }

                QSlider::groove:horizontal {
                    background-color: #d5d5d5;
                    height: 10px;
                }

                QSlider::handle:horizontal {
                    background-color: #000000;
                    width: 10px;
                    margin: -5px;
                }
            ''')

    def update_auto_timer(self, state):
        if state == Qt.Checked:
            self.setup_auto_timer()
        else:
            self.disable_auto_timer()

    def update_slide_time_label(self, value):
        hours = value // 60
        minutes = value % 60
        self.slide_time_label.setText(f'Slide Time: {hours} hours {minutes} minutes')

    def choose_background(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog(self, 'Choose Background', options=options)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilters(["Image files (*.png *.jpg *.jpeg)", "Folder"])
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if len(selected_files) > 0:
                selected_file = selected_files[0]
                if len(selected_files) == 1 and not selected_file.endswith(('png', 'jpg', 'jpeg')):
                    self.background_folder_lineEdit = selected_file
                    self.background_image_lineEdit = None
                else:
                    self.background_image_lineEdit = selected_file
                    self.background_folder_lineEdit = None
                self.update_preview()

    def update_preview(self):
        if self.background_image_lineEdit:
            pixmap = QPixmap(self.background_image_lineEdit)
        elif self.background_folder_lineEdit:
            image_files = [
                file for file in os.listdir(self.background_folder_lineEdit)
                if file.endswith(('.png', '.jpg', '.jpeg'))
            ]
            if image_files:
                first_image_path = os.path.join(self.background_folder_lineEdit, image_files[0])
                pixmap = QPixmap(first_image_path)
            else:
                pixmap = QPixmap()  # Empty pixmap if no images found
        else:
            pixmap = QPixmap()  # Empty pixmap if no selection

        if pixmap.isNull() or pixmap.width() == 0 or pixmap.height() == 0:
            self.preview_label.clear()  # Clear the label if pixmap is null or empty
        else:
            self.preview_label.setPixmap(pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio))

    def setup_auto_timer(self):
        if hasattr(self, 'auto_timer'):
            self.auto_timer.stop()

        slide_time_minutes = self.slide_time_slider.value()
        slide_time_milliseconds = slide_time_minutes * 60 * 1000  # Convert minutes to milliseconds
        self.auto_timer = QTimer(self)
        self.auto_timer.timeout.connect(self.launch_lock_dialog)
        self.auto_timer.start(slide_time_milliseconds)

    def disable_auto_timer(self):
        if hasattr(self, 'auto_timer'):
            self.auto_timer.stop()

    def launch_lock_dialog(self):
        lock_dialog = LockDialog(self)
        lock_dialog.exec_()

    def load_settings(self):
        try:
            self.settings = QSettings("MyApp", "ScreenLocker")
            background_image = self.settings.value('background_image')
            if background_image:
                self.background_image_lineEdit = background_image

            background_folder = self.settings.value('background_folder')
            if background_folder:
                self.background_folder_lineEdit = background_folder

            auto_timer = self.settings.value('auto_timer')
            if auto_timer:
                self.auto_timer_checkbox.setChecked(bool(auto_timer))

            slide_time = self.settings.value('slide_time')
            if slide_time:
                self.slide_time_slider.setValue(int(slide_time))

            self.update_preview()
        except Exception as e:
            print(f"Error loading settings: {e}")

    def save_settings(self):
        try:
            self.settings.setValue('background_image', self.background_image_lineEdit)
            self.settings.setValue('background_folder', self.background_folder_lineEdit)
            self.settings.setValue('auto_timer', self.auto_timer_checkbox.isChecked())
            self.settings.setValue('slide_time', self.slide_time_slider.value())
            self.accept()
        except Exception as e:
            self.settings_logger.error(f"Error saving settings: {str(e)}")

    def create_credentials(self):
        try:
            if len(self.user_credentials) >= 2:
                QMessageBox.warning(self, 'Credentials Limit', 'You have reached the maximum number of credentials.')
                return

            username, ok = QInputDialog.getText(self, 'Create User Credentials', 'Enter username:')
            if ok:
                for user in self.user_credentials:
                    if user[0] == username:
                        QMessageBox.warning(self, 'Username Exists', 'The entered username already exists.')
                        return

                password, ok = QInputDialog.getText(self, 'Create User Credentials', 'Enter password:', QLineEdit.Password)
                if ok:
                    self.user_credentials.append((username, password))
                    self.save_user_credentials()
        except Exception as e:
            print(f"Error creating credentials: {e}")

    def change_password(self):
        try:
            users = [user[0] for user in self.user_credentials]
            if users:
                selected_user, ok = QInputDialog.getItem(self, 'Change Password', 'Select user:', users, editable=False)
                if ok:
                    new_password, ok = QInputDialog.getText(self, 'Change Password', 'Enter new password:', QLineEdit.Password)
                    if ok:
                        for i, user in enumerate(self.user_credentials):
                            if user[0] == selected_user:
                                self.user_credentials[i] = (selected_user, new_password)
                                self.save_user_credentials()
        except Exception as e:
            print(f"Error changing password: {e}")

    def save_user_credentials(self):
        try:
            filename = 'credentials.csv'
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['username', 'password'])
                writer.writerows(self.user_credentials)
        except Exception as e:
            self.settings_logger.error(f"Error saving user credentials: {str(e)}")


    def load_user_credentials(self):
        try:
            filename = 'credentials.csv'
            with open(filename, 'r', newline='') as file:
                reader = csv.reader(file)
                user_credentials = [row for row in reader if len(row) == 2]
                return user_credentials
        except Exception as e:
            self.settings_logger.error(f"Error loading user credentials: {str(e)}")
            return []

    # Rest of the code...

    def load_settings(self):
        try:
            self.settings = QSettings("MyApp", "ScreenLocker")
            background_image = self.settings.value('background_image')
            if background_image:
                self.background_image_lineEdit = background_image

            background_folder = self.settings.value('background_folder')
            if background_folder:
                self.background_folder_lineEdit = background_folder

            auto_timer = self.settings.value('auto_timer')
            if auto_timer:
                self.auto_timer_checkbox.setChecked(bool(auto_timer))

            slide_time = self.settings.value('slide_time')
            if slide_time:
                self.slide_time_slider.setValue(int(slide_time))

            self.update_preview()
        except Exception as e:
            self.settings_logger.exception(f"Error loading settings: {str(e)}")


    def save_settings(self):
        try:
            self.settings.setValue('background_image', self.background_image_lineEdit)
            self.settings.setValue('background_folder', self.background_folder_lineEdit)
            self.settings.setValue('auto_timer', self.auto_timer_checkbox.isChecked())
            self.settings.setValue('slide_time', self.slide_time_slider.value())

            self.accept()
        except Exception as e:
            self.settings_logger.exception(f"Error saving settings: {str(e)}")

    def create_credentials(self):
        try:
            if len(self.user_credentials) >= 2:
                QMessageBox.warning(self, 'Credentials Limit', 'You have reached the maximum number of credentials.')
                return

            username, ok = QInputDialog.getText(self, 'Create User Credentials', 'Enter username:')
            if ok:
                for user in self.user_credentials:
                    if user[0] == username:
                        QMessageBox.warning(self, 'Username Exists', 'The entered username already exists.')
                        return

                password, ok = QInputDialog.getText(self, 'Create User Credentials', 'Enter password:', QLineEdit.Password)
                if ok:
                    self.user_credentials.append((username, password))
                    self.save_user_credentials()
        except Exception as e:
            self.settings_logger.exception(f"Error creating credentials: {e}")

    def change_password(self):
        try:
            users = [user[0] for user in self.user_credentials]
            if users:
                selected_user, ok = QInputDialog.getItem(self, 'Change Password', 'Select user:', users, editable=False)
                if ok:
                    new_password, ok = QInputDialog.getText(self, 'Change Password', 'Enter new password:', QLineEdit.Password)
                    if ok:
                        for i, user in enumerate(self.user_credentials):
                            if user[0] == selected_user:
                                self.user_credentials[i] = (selected_user, new_password)
                                self.save_user_credentials()
        except Exception as e:
            self.logger.exception(f"Error changing password: {e}")

    def save_user_credentials(self):
        try:
            filename = 'credentials.csv'
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['username', 'password'])
                writer.writerows(self.user_credentials)
        except Exception as e:
            self.logger.exception(f"Error saving user credentials: {e}")

    def load_user_credentials(self):
        try:
            filename = 'credentials.csv'
            with open(filename, 'r', newline='') as file:
                reader = csv.reader(file)
                user_credentials = [row for row in reader if len(row) == 2]
                return user_credentials
        except (FileNotFoundError, csv.Error):
            return []

    
#-------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------




class Login(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")

        layout = QVBoxLayout()

        label_username = QLabel("Username:")
        self.input_username = QLineEdit()
        layout.addWidget(label_username)
        layout.addWidget(self.input_username)

        label_password = QLabel("Password:")
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(label_password)
        layout.addWidget(self.input_password)

        button_login = QPushButton("Login")
        button_login.clicked.connect(self.login)
        layout.addWidget(button_login)

        self.setLayout(layout)

        self.setStyleSheet(
            """
            QDialog {
                background-color: #ECECEC;
            }

            QLabel {
                color: #333333;
            }

            QLineEdit {
                background-color: white;
                color: #333333;
            }

            QPushButton {
                background-color: #007BFF;
                color: white;
            }
            """
        )

    def login(self):
        username = self.input_username.text()
        password = self.input_password.text()

        # Perform login authentication logic
        if self.authenticate(username, password):
            QMessageBox.information(self, "Welcome back", "Login successful. Welcome back!")
            self.accept()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")

    def authenticate(self, username, password):
        # Load credentials from a CSV file
        with open("credentials.csv", "r") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == username and row[1] == password:
                    return True
        return False




class LockDialog(QDialog):
    def __init__(self, ):
        super().__init__()
        # Rest of your code

        self.setWindowTitle("Lock Screen")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.SplashScreen)
        self.setStyleSheet("background-color: black;")

        layout = QVBoxLayout()
        label = QLabel("Locked")
        label.setStyleSheet("font-size: 24px; color: white;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.setLayout(layout)

        self.setLocked(True)

    def setLocked(self, locked):
        if locked:
            self.mousePressEvent = self.showLoginWindow
        else:
            self.mousePressEvent = None

    def showLoginWindow(self, event):
        login_dialog = Login(self)
        if login_dialog.exec_() == QDialog.Accepted:
            self.setLocked(False)
            self.show()
            self.close()


    def showEvent(self, event):
        # Set the dialog size to match the screen size
        desktop = QApplication.desktop()
        screen_rect = desktop.screenGeometry()
        self.setGeometry(screen_rect)
        
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape or key == Qt.Key_Q:
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
