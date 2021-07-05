import PyQt5.QtWidgets as QtWidgets
from .GuiPlugin import GuiPlugin
from .GuiMonitorPlugin import GuiMonitorPlugin


class App(QtWidgets.QWidget):

    def __init__(self, plugins, monitor_plugins):
        super().__init__()
        self.setWindowTitle("Miner Manager")
        self.plugins = plugins
        self.monitor_plugins = monitor_plugins

        self.layout = QtWidgets.QGridLayout()

        for i, plugin in enumerate(self.plugins):
            self.__dict__[plugin.name] = GuiPlugin(self, plugin, i)
            self.__dict__[plugin.name].add_gui_row()

        self.start_programs_btn = QtWidgets.QPushButton("Start All Programs")
        self.start_programs_btn.clicked.connect(self.start_all_programs)
        self.layout.addWidget(self.start_programs_btn, len(self.plugins), 1, 1, 2)

        # Empty row
        self.layout.addWidget(QtWidgets.QLabel(""), len(self.plugins) + 1, 1, 1, 2)

        for i, monitor_plugin in enumerate(self.monitor_plugins):
            self.__dict__[monitor_plugin.name] = GuiMonitorPlugin(self, monitor_plugin, i + len(self.plugins) + 2)
            self.__dict__[monitor_plugin.name].add_gui_row()
            
        self.start_monitors_btn = QtWidgets.QPushButton("Start Selected Monitors")
        self.start_monitors_btn.clicked.connect(self.start_all_monitors)
        self.layout.addWidget(self.start_monitors_btn, len(self.plugins) + len(self.monitor_plugins) + 2, 0, 1, 2)

        self.stop_monitors_btn = QtWidgets.QPushButton("Stop Running Monitors")
        self.stop_monitors_btn.clicked.connect(self.stop_all_monitors)
        self.layout.addWidget(self.stop_monitors_btn, len(self.plugins) + len(self.monitor_plugins) + 2, 2, 1, 2)
        
        self.setLayout(self.layout)

    def start_all_programs(self):
        # Update status info
        for p in self.plugins:
            p.update_status()

        # Start non running programs
        for p in self.plugins:
            if not p.running:
                p.start()

        # Set foregrounf
        for p in self.plugins:
            p.set_foreground()
        
    def start_all_monitors(self):
        self.start_monitors_btn.text = "Stop All Monitors"
        for m in self.monitor_plugins:
            monitor = self.__dict__[m.name]
            if monitor.enabled and not monitor.running:
                monitor.start_plugin()

    def stop_all_monitors(self):
        self.start_monitors_btn.text = "Start All Monitors"
        for m in self.monitor_plugins:
            monitor = self.__dict__[m.name]
            if monitor.running:
                monitor.stop_plugin()


def start(plugins, monitors):
    app = QtWidgets.QApplication([])
    app.setStyle('Fusion')

    window = App(plugins, monitors)

    window.show()
    app.exec_()
    # sys.exit(app.exec_())
