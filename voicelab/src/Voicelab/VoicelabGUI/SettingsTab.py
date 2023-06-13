from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from .VoicelabTab import VoicelabTab
from ..default_settings import function_requirements
import types
import copy




class SettingsTab(VoicelabTab):
    """SettingsTab(VoicelabTab) : presentation widget for displaying and controlling the settings for processing the
    voice files. inherits basic functionality from the VoicelabTab base tab class"""
    def __init__(self, data_controller, signals, tabs, *args, **kwargs):

        """
        Args:
            data_controller:
            signals:
            tabs:
            *args:
            **kwargs:
        """
        super().__init__(data_controller, signals, tabs, *args, **kwargs)

        self.signals["on_files_changed"].connect(self.on_files_changed)

        # stores the current, cached, and default values for what line edits should be checked
        self.checked_state = {"active": {}, "default": {}, "cached": {}, "required": {}}

        # configure base state for check values
        for fn_name in self.data_controller.loaded_functions:

            if fn_name in self.data_controller.default_functions:
                self.checked_state["active"][fn_name] = Qt.PartiallyChecked
                self.checked_state["default"][fn_name] = Qt.PartiallyChecked
                self.checked_state["cached"][fn_name] = Qt.PartiallyChecked

            else:
                self.checked_state["active"][fn_name] = Qt.Unchecked
                self.checked_state["default"][fn_name] = Qt.Unchecked
                self.checked_state["cached"][fn_name] = Qt.Unchecked

        self.data_controller.save_state()
        self.initUI()

    def initUI(self):
        """initUI: pyqt widget function, called to draw the widgets to the screen"""
        self.layout = QVBoxLayout()

        self.is_active = True
        self.advanced_toggle = QCheckBox("Use Advanced Settings")
        self.advanced_toggle.stateChanged.connect(self.toggle_advanced_settings)

        self.btn_start = QPushButton("Start")
        self.btn_start.clicked.connect(self.onclick_start)
        self.btn_start.setDisabled(True)
        self.progress = QProgressBar()

        self.measure_settings = MeasureSettings(
            self.data_controller, self.checked_state
        )
        self.measure_settings.set_fn_checked_state(self.checked_state["active"])
        self.layout.addWidget(self.advanced_toggle)
        self.layout.addWidget(self.measure_settings)
        self.layout.addWidget(self.btn_start)
        self.layout.addWidget(self.progress)

        self.measure_settings.setDisabled(self.is_active)
        self.setLayout(self.layout)

    ###############################################################################################
    # callback for when a single node is run
    ###############################################################################################
    def on_progress_updated(self, node, start, current, end):
        """
        Args:
            node:
            start:
            current:
            end:
        """
        self.progress.setValue(current)
        print(node, start, current, end)

    ###############################################################################################
    # callback for when files change
    ###############################################################################################
    def on_files_changed(self, file_paths):
        """
        Args:
            file_paths:
        """
        if len(file_paths) > 0:
            self.btn_start.setDisabled(False)
        else:
            self.btn_start.setDisabled(True)

    ###############################################################################################
    # Turn the use of advanced settings on and off
    ###############################################################################################
    def toggle_advanced_settings(self, checked):

        # When advanced settings is turned off, we want to run and the display the defaults
        """
        Args:
            checked:
        """
        if checked == Qt.Unchecked:
            # save the check values so we can easily swap them back in later
            self.checked_state["cached"] = self.checked_state["active"]
            self.checked_state["active"] = self.checked_state["default"]

            # save the state in the data model and reset back to the defaults
            self.data_controller.save_state()
            self.data_controller.reset_active_settings()
            self.data_controller.reset_active_functions()

        # When advanced settings is turned on, we want to run and display the custom settings
        elif checked == Qt.Checked:
            self.checked_state["active"] = self.checked_state["cached"]
            self.data_controller.load_state()

        # Enable or disable the settings widget
        self.measure_settings.setDisabled(not bool(checked))
        self.measure_settings.set_fn_checked_state(self.checked_state["active"])

    ###############################################################################################
    # onclick_start: callback for when the start button is clicked. Starts the pipeline processing
    ###############################################################################################
    def onclick_start(self):
        self.data_controller.reset_figures()
        n_voices = len(self.data_controller.active_voices)
        n_functions = len(self.data_controller.active_functions) + 1
        self.progress.setMinimum(0)
        self.progress.setMaximum(n_voices * n_functions)
        self.signals["on_progress_update"].connect(self.on_progress_updated)

        self.start_process()

        self.tabs.setCurrentIndex(2)


###################################################################################################
# MeasureSettings::QWidget
## handles the presentation for selecting and configuring functions
###################################################################################################


class MeasureSettings(QWidget):
    def __init__(self, data_controller, checked_state, *args, **kwargs):

        """
        Args:
            data_controller:
            checked_state:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)
        self.data_controller = data_controller
        self.checked_state = checked_state
        self.existing_stack = None
        self.model = None

        self.measure_layout = QVBoxLayout()
        self.measure_list = QListWidget()
        self.measure_stack = QStackedWidget()

        self.list_stacks = {}
        self.stack_layouts = {}
        self.stack = QStackedWidget(self)

        self.reset_defaults = QPushButton()
        self.reset_defaults.setText("Reset all to defaults")
        self.reset_defaults.clicked.connect(self.on_reset)

        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)

        self.list_items = {}
        self.leftlist = QListWidget()

        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self.select_all)

        self.select_none_btn = QPushButton("Select None")
        self.select_none_btn.clicked.connect(self.select_none)

        left_layout.addWidget(self.leftlist)
        left_layout.addWidget(self.select_all_btn)
        left_layout.addWidget(self.select_none_btn)
        left_layout.addWidget(self.reset_defaults)

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(left_widget)
        self.layout.addWidget(self.stack)

        self.setLayout(self.layout)
        self.initUI()
        self.leftlist.currentRowChanged.connect(self.display)
        self.leftlist.itemChanged.connect(self.onchange_check)
        self.set_fn_checked_state(self.checked_state["default"])

    def select_all(self):
        for fn_name in self.data_controller.loaded_functions:
            self.data_controller.activate_function(fn_name)
            self.checked_state["active"][fn_name] = Qt.Checked

        self.set_fn_checked_state(self.checked_state["active"])

    def select_none(self):
        for fn_name in self.data_controller.loaded_functions:
            self.data_controller.deactivate_function(fn_name)
            self.checked_state["active"][fn_name] = Qt.Unchecked

        self.set_fn_checked_state(self.checked_state["active"])

    ###############################################################################################
    # set_fn_checked_state : set the checked state of the function lists
    ###############################################################################################
    def set_fn_checked_state(self, check_states):
        """
        Args:
            check_states:
        """
        self.leftlist.itemChanged.disconnect()
        list_edits = self.list_items
        for fn_name in list_edits:
            list_edits[fn_name].setCheckState(check_states[fn_name])
        # self.leftlist.update()
        self.leftlist.itemChanged.connect(self.onchange_check)

    ###############################################################################################
    # display_options
    ###############################################################################################

    def initUI(self):

        active_settings = self.data_controller.active_settings

        for fn_name in active_settings:

            # Add this option to the list with appropriate text and checkbox
            self.list_items[fn_name] = QListWidgetItem(parent=self.leftlist)
            self.list_items[fn_name].setText(fn_name)

            # Add the appropriate configuration widgets
            self.list_stacks[fn_name] = QWidget()
            self.stack.addWidget(self.list_stacks[fn_name])
            # self.stack_layouts[fn_name] = QFormLayout()
            self.stack_layouts[fn_name] = QVBoxLayout()
            self.stack_layouts[fn_name].setAlignment(Qt.AlignTop)

            if len(active_settings[fn_name]) == 0:
                label = QLabel()
                label.setText("No settings to configure")
                self.stack_layouts[fn_name].addWidget(label)
            else:
                for parameter in active_settings[fn_name]:
                    param_value = active_settings[fn_name][parameter]

                    # If there are options, display them as a combo box
                    if isinstance(param_value, tuple):
                        widget = ComboSetting(
                            parameter,
                            param_value,
                            fn_name,
                            self.data_controller,
                            model=self.model,
                        )
                        self.stack_layouts[fn_name].addWidget(widget)

                    elif isinstance(param_value, bool):
                        widget = CheckSettingWidget(
                            parameter,
                            param_value,
                            fn_name,
                            self.data_controller,
                            model=self.model,
                        )
                        self.stack_layouts[fn_name].addWidget(widget)

                    # Otherwise just assume some sort of text input
                    elif not callable(param_value):
                        widget = SettingWidget(
                            parameter,
                            param_value,
                            fn_name,
                            self.data_controller,
                            model=self.model,
                        )
                        self.stack_layouts[fn_name].addWidget(widget)

            self.list_stacks[fn_name].setLayout(self.stack_layouts[fn_name])

    ###############################################################################################
    # on change check: Callback function for when a setting checkbox is ticked
    ###############################################################################################
    def onchange_check(self, e):
        """
        Args:
            e:
        """
        fn_name = e.text()
        if e.checkState():
            self.data_controller.activate_function(fn_name)
            if fn_name in function_requirements:
                for parent_fn, parent_label in function_requirements[fn_name]:
                    if parent_fn not in self.checked_state["required"]:
                        self.checked_state["required"][parent_fn] = 0

                    self.checked_state["required"][parent_fn] = (
                        self.checked_state["required"][parent_fn] + 1
                    )

                    if self.checked_state["active"][parent_fn] == Qt.Unchecked:
                        self.data_controller.activate_function(parent_fn)
                        self.checked_state["active"][parent_fn] = Qt.PartiallyChecked
                        self.list_items[parent_fn].setCheckState(Qt.PartiallyChecked)
        else:
            self.data_controller.deactivate_function(fn_name)

            if fn_name in function_requirements:
                for parent_fn, parent_label in function_requirements[fn_name]:
                    self.checked_state["required"][parent_fn] = (
                        self.checked_state["required"][parent_fn] - 1
                    )
                    if self.list_items[parent_fn].checkState() == Qt.PartiallyChecked:
                        if self.checked_state["required"][parent_fn] <= 0:
                            self.data_controller.deactivate_function(parent_fn)
                            self.checked_state["active"][parent_fn] = Qt.Unchecked
                            self.list_items[parent_fn].setCheckState(Qt.Unchecked)

        self.checked_state["active"][fn_name] = e.checkState()

    def display(self, i):
        """
        Args:
            i:
        """
        self.stack.setCurrentIndex(i)

    def on_reset(self):

        self.data_controller.reset_active_functions()
        print(self.data_controller.active_functions)
        self.checked_state["active"] = copy.copy(self.checked_state["default"])
        # self.initUI()
        self.set_fn_checked_state(self.checked_state["active"])


class SettingWidget(QWidget):
    def __init__(
        self, name, default, fn_name, data_controller, model=None, *args, **kwargs
    ):
        """
        Args:
            name:
            default:
            fn_name:
            data_controller:
            model:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)
        self.bad_inputs = {" ", ",", ".", ":", ";", "!", "?", "'", "\\", "/", "", "-", '_', '+', '=', '*', '&', '^',
                           '%', '$', '#', '@', '~', '`', '<', '>', '|', '{', '}', '[', ']', '(', ')', '"', '\''}

        self.data_controller = data_controller

        self.default = default
        self.inactive = True
        self.cached = default
        self.model = model
        self.name = name
        self.type = type(default)
        self.fn_name = fn_name

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel()
        self.label.setText(str(name))

        self.checkbox = QCheckBox()
        self.checkbox.stateChanged.connect(self.toggle)
        self.lineedit = QLineEdit()
        self.lineedit.setDisabled(self.inactive)
        self.lineedit.setText(str(self.default))
        self.lineedit.textChanged.connect(self.on_textchanged)

        if isinstance(self.default, int):
            self.lineedit.setValidator(QIntValidator())

        if isinstance(self.default, float):
            self.lineedit.setValidator(QDoubleValidator())

        self.layout.addWidget(self.checkbox)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.lineedit)

    # Toggle resets the control widget and it's bound value to the default settings
    def toggle(self, e):
        """
        Args:
            e:
        """
        self.inactive = not self.inactive
        self.lineedit.setDisabled(self.inactive)
        if self.inactive:
            self.cached = self.lineedit.text()
            self.lineedit.setText(str(self.default))
            self.data_controller.reset_setting(self.fn_name, self.name)
        else:
            self.lineedit.setText(str(self.cached))
            self.data_controller.set_settings(self.fn_name, [self.name], [self.cached])

    def reset(self):
        self.bound_variable = self.default
        self.cached = self.default
        self.inactive = True

    def on_textchanged(self, new_text):
        """
        Args:
            new_text:
        """

        setting_type = type(self.default)
        if new_text not in self.bad_inputs:
            self.data_controller.set_settings(
                self.fn_name, [self.name], [setting_type(new_text)]
            )


    @property
    def value(self):
        return self.lineedit.text()


class FunctionSetting(QWidget):
    def __init__(
        self, name, default, fn_name, data_controller, model=None, *args, **kwargs
    ):
        """
        Args:
            name:
            default:
            fn_name:
            data_controller:
            model:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)

        self.data_controller = data_controller
        self.name = name
        self.model = model
        self.fn_name = fn_name
        self.inactive = True
        self.cached = ""
        self.default = default
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel()
        self.label.setText(str(name))

        self.checkbox = QCheckBox()
        self.checkbox.stateChanged.connect(self.toggle)
        self.lineedit = QLineEdit()
        self.lineedit.setDisabled(self.inactive)
        self.lineedit.setText("Automatic")

        self.layout.addWidget(self.checkbox)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.lineedit)

    def toggle(self, e):
        """
        Args:
            e:
        """
        self.inactive = not self.inactive
        self.lineedit.setDisabled(self.inactive)

        if self.inactive:
            self.cached = self.lineedit.text()
            self.lineedit.setText("Automatic")
            # self.model['settings'][self.fn_name]['value'][self.name] = self.default
            self.data_controller.reset_setting(self.fn_name, self.name)

        else:
            self.lineedit.setText(self.cached)
            # self.model['settings'][self.fn_name]['value'][self.name] = self.cached
            self.data_controller.set_settings(self.fn_name, [self.name], [self.cached])

    # New stuff DRF
    def line_edit(self):
        return self.lineedit.text()

    @property
    def value(self):
        if self.inactive:
            return self.default
        # Changed to remove lambdas
        #return lambda: self.lineedit.text()
        return self.lineedit


class ComboSetting(QWidget):
    def __init__(
        self, name, default, fn_name, data_controller, model=None, *args, **kwargs
    ):
        """
        Args:
            name:
            default:
            fn_name:
            data_controller:
            model:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)

        self.data_controller = data_controller
        self.default = default[0]
        self.inactive = True
        self.cached = self.default
        self.model = model
        self.name = name
        self.fn_name = fn_name

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel()
        self.label.setText(str(name))
        self.label.setAlignment(Qt.AlignLeft)

        self.checkbox = QCheckBox()
        self.checkbox.stateChanged.connect(self.toggle)

        self.combobox = QComboBox()
        self.combobox.setSizePolicy(
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        )

        for item in default[1]:
            self.combobox.addItem(item)

        self.combobox.setCurrentText(self.default)
        self.combobox.setDisabled(self.inactive)
        self.combobox.currentIndexChanged.connect(self.on_statechanged)

        self.layout.addWidget(self.checkbox)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.combobox)

    def toggle(self, e):

        """
        Args:
            e:
        """
        self.inactive = not self.inactive
        self.combobox.setDisabled(self.inactive)

        if self.inactive:
            self.cached = self.combobox.currentText()
            self.combobox.setCurrentText(str(self.default))
            # self.model['settings'][self.fn_name]['value'][self.name] = self.default
            self.data_controller.set_settings(self.fn_name, [self.name], [self.default])

        else:
            self.combobox.setCurrentText(str(self.cached))
            # self.model['settings'][self.fn_name]['value'][self.name] = self.cached
            self.data_controller.set_settings(self.fn_name, [self.name], [self.cached])

    def on_statechanged(self, e):
        """
        Args:
            e:
        """
        self.data_controller.set_settings(
            self.fn_name, [self.name], [type(self.default)(self.combobox.currentText())]
        )

    @property
    def value(self):
        return self.combobox.currentText()


class CheckSettingWidget(QWidget):
    def __init__(
        self, name, default, fn_name, data_controller, model=None, *args, **kwargs
    ):
        """
        Args:
            name:
            default:
            fn_name:
            data_controller:
            model:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)

        self.data_controller = data_controller
        self.default = default
        self.inactive = True
        self.cached = self.default
        self.model = model
        self.name = name
        self.fn_name = fn_name

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel()
        self.label.setText(str(name))
        self.label.setAlignment(Qt.AlignLeft)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(self.default)
        self.checkbox.stateChanged.connect(self.toggle)

        self.layout.addWidget(self.checkbox)
        self.layout.addWidget(self.label)

    def toggle(self, e):
        """
        Args:
            e:
        """
        self.data_controller.set_settings(
            self.fn_name, [self.name], [self.checkbox.isChecked()]
        )
        # self.inactive = not self.inactive

        # if self.inactive:
        #     self.cached = self.checkbox.isChecked()
        #     # self.model['settings'][self.fn_name]['value'][self.name] = self.default
        #     self.data_controller.set_settings(self.fn_name, [self.name], [self.default])

        # else:
        #     # self.checkbox.setChecked(bool(self.cached))
        #     # self.model['settings'][self.fn_name]['value'][self.name] = self.cached
        #     self.data_controller.set_settings(self.fn_name, [self.name], [self.cached])

    @property
    def value(self):
        return self.checkbox.isChecked()
