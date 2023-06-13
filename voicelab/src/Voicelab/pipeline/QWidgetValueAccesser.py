from PyQt5.QtWidgets import *


class QWidgetValueAccesser:
    def get_value(self, widget):
        """
        Args:
            widget:
        """
        if isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, QLineEdit):
            return widget.text()
        elif isinstance(widget, QCheckBox):
            return widget.isChecked()

    def set_value(self, widget, value):
        """
        Args:
            widget:
            value:
        """
        if isinstance(widget, QComboBox):
            widget.setCurrentText(value)
        elif isinstance(widget, QLineEdit):
            widget.setText(value)
        elif isinstance(widget, QCheckBox):
            widget.setChecked(value)
