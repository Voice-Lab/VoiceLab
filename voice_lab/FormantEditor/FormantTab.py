import sys
from PyQt5.QtWidgets import *
from spectrogramCanvas import SpectrogramCanvas


class ApplicationWindow(QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.initialize_main_widget()

    def initialize_main_widget(self):
        self.setWindowTitle("Formant Editor")
        self.zoom_mode_enabled = False  
        # Create the main widget
        self.main_widget = QWidget(self)
        
        # Create a layout for the main widget
        self.layout = QVBoxLayout(self.main_widget)

        # Create the canvas
        self.sc = SpectrogramCanvas(self.main_widget, dpi=100)

        # create a scrollable area for scroll bars on the canvas
        scroll = QScrollArea(self.main_widget)
        scroll.setWidget(self.sc)
        # The canvas size is fixed; it does not resize with the window
        scroll.setWidgetResizable(False)
        self.layout.addWidget(scroll)

        # Add buttons to the canvas
        self.add_buttons()  

        # resize the main window
        self.setCentralWidget(self.main_widget)
        self.resize(1000, 800)  # Initial window size, adjust as needed
    

    def add_buttons(self):
        # Add buttons for zoom and save functionality
        self.zoom_out_button = QPushButton('Zoom out to original scale')
        self.zoom_out_button.clicked.connect(self.sc.reset_zoom)
        self.layout.addWidget(self.zoom_out_button)

        self.save_button = QPushButton('Save and Finish')
        self.save_button.clicked.connect(self.save_and_finish)
        self.layout.addWidget(self.save_button)

        self.toggle_zoom_mode_button = QPushButton('Enable Zoom Mode')
        self.toggle_zoom_mode_button.clicked.connect(self.sc.toggle_zoom_mode_canvas)
        self.layout.addWidget(self.toggle_zoom_mode_button)

    def toggle_zoom_mode(self):

        self.zoom_mode_enabled = not self.zoom_mode_enabled
        # Update UI elements as necessary, for example:
        if self.zoom_mode_enabled:
            self.toggle_zoom_mode_button.setText("Disable Zoom Mode")
        else:
            self.toggle_zoom_mode_button.setText("Enable Zoom Mode")

    def resizeEvent(self, event):
        # Ensure the base class resize event is called
        super(ApplicationWindow, self).resizeEvent(event)  

    def save_and_finish(self):
        # Implement save functionality here
        print("Save and Finish clicked")
        self.close()




app = QApplication(sys.argv)
window = ApplicationWindow()
window.show()
sys.exit(app.exec_())
