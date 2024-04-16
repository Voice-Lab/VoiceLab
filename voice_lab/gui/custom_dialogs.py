from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
from PyQt6.QtCore import QSize


class PraatInfoDialog(QDialog):
    def __init__(self, info_object, parent=None):
        """Dialog for displaying information about a Praat sound object.
        Args:
            info_object: The object containing the information to display.
            parent: The parent widget of the dialog.
        """
        super().__init__(parent)
        self.setWindowTitle("Praat Voice Information")
        layout = QVBoxLayout()

        # Create a text edit for displaying information
        self.infoDisplay = QTextEdit()
        self.infoDisplay.setReadOnly(True)
        
        # Set the fixed size or minimum size of the QTextEdit
        self.infoDisplay.setFixedSize(QSize(400, 500))  # Set a fixed size
        # Alternatively, set a minimum size to allow resizing up to a certain point
        # self.infoDisplay.setMinimumSize(QSize(400, 300))

        self.format_and_display_info(info_object)
        layout.addWidget(self.infoDisplay)
        
        #Add a close button for the dialog
        closeButton = QPushButton("Close")
        closeButton.clicked.connect(self.close)
        layout.addWidget(closeButton)

        self.setLayout(layout)
    
    def format_and_display_info(self, info_object):
        # Assuming info_object can be converted to a string with meaningful information
        info_text = str(info_object)

        # Check for specific attributes and format them
        if hasattr(info_object, 'duration'):
            info_text += f"\nDuration: {info_object.duration:.2f} seconds"
        
        # You can add more formatting based on the attributes of info_object
        # Example: if it's a dictionary or has multiple attributes, format them line by line
        if hasattr(info_object, '__dict__'):
            for key, value in info_object.__dict__.items():
                info_text += f"\n{key.capitalize()}: {value}"

        self.infoDisplay.setText(info_text)
