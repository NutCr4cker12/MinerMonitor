import logging
from threading import Timer
from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QCheckBox
)

class GuiPlugin:

    def __init__(self, parent, plugin, row):
        self.parent = parent
        self.plugin = plugin
        self.name = plugin.name
        self.running = plugin.running
        self.row = row
        self.runner = None

        self.label = QLabel(self.name)
        self.action_button = QPushButton("")
        self.action_button.clicked.connect(self.toggle_run)
        self.foreground_button = QPushButton("Show")
        self.foreground_button.clicked.connect(self.set_foreground)
        self.status_label = QLabel("")

        self.plugin.update_callback = self.update_status
        self.update_status()

    def add_gui_row(self):
        self.parent.layout.addWidget(self.label, self.row, 0)
        self.parent.layout.addWidget(self.action_button, self.row, 1)
        self.parent.layout.addWidget(self.foreground_button, self.row, 2)
        self.parent.layout.addWidget(self.status_label, self.row, 3)

    def update_status(self):
        logging.info(f"{self.name} - Updating status")
        if self.plugin.running:
            self.status_label.setText("Running...")
            self.action_button.setText("Stop")
        else:
            self.status_label.setText("")
            self.action_button.setText("Start")

    def toggle_run(self):
        if self.plugin.running:
            self.stop()
        else:
            self.start()

    def set_foreground(self):
        self.plugin.set_foreground()
        self.update_status()

    def start(self):
        logging.info(f"{self.name} - starting...")

        self.runner = Timer(0.1, self.plugin.start)
        self.runner.start()
        logging.info(f"{self.name} - started")
        self.runner.join()
        # self.update_status()

    def stop(self):
        logging.info(f"{self.name} stopping...")

        self.plugin.stop()

        # self.running = False
        if self.runner is not None:
            logging.info(f"{self.name}: waiting for program to stop..")
            self.runner.join()

        logging.info(f"{self.name} stopped.")
        # self.update_status()
