import PyQt5.QtWidgets as QtWidgets
from .GuiPlugin import GuiPlugin


class App(QtWidgets.QWidget):

    def __init__(self, plugins):
        super().__init__()
        self.setWindowTitle("Miner Manager")
        self.plugins = plugins

        self.layout = QtWidgets.QGridLayout()

        for i, plugin in enumerate(self.plugins):
            self.__dict__[plugin.name] = GuiPlugin(self, plugin, i)
            self.__dict__[plugin.name].add_gui_row()

        self.start_programs_btn = QtWidgets.QPushButton("Start")
        self.start_programs_btn.clicked.connect(self.start_all_programs)
        self.layout.addWidget(self.start_programs_btn, len(self.plugins), 1, 1, 2)
        
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
        


def start(plugins):
    app = QtWidgets.QApplication([])
    app.setStyle('Fusion')

    window = App(plugins)

    window.show()
    app.exec_()
    # sys.exit(app.exec_())
