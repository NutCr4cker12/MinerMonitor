from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QCheckBox
)

class GuiMonitorPlugin:

    def __init__(self, parent, monitor_plugin, row):
        self.parent = parent
        self.monitor_plugin = monitor_plugin
        self.name = monitor_plugin.name
        self.row = row
        
        self.running = False
        self.check_box = QCheckBox(self.name)
        self.check_box.setChecked(self.monitor_plugin.defaultEnabled)
        self.toggle_run_btn = QPushButton("Start")
        self.toggle_run_btn.clicked.connect(self.toggle_run)
        self.status_label = QLabel("")

    def add_gui_row(self):
        self.parent.layout.addWidget(self.check_box, self.row, 0)
        self.parent.layout.addWidget(self.toggle_run_btn, self.row, 1)
        self.parent.layout.addWidget(self.status_label, self.row, 3)

    def toggle_run(self):
        if self.running:
            self.stop_plugin()
        else:
            self.start_plugin()

    def start_plugin(self):
        self.monitor_plugin.start()
        self.check_box.setDisabled(True)
        self.toggle_run_btn.setText("Stop")
        self.status_label.setText("Running...")
        self.running = True

    def stop_plugin(self):
        self.monitor_plugin.kill()
        self.check_box.setDisabled(False)
        self.toggle_run_btn.setText("Start")
        self.status_label.setText("")
        self.running = False

    @property
    def enabled(self):
        return self.check_box.isChecked()