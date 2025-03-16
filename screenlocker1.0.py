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
