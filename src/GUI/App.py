import sys
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

        self.setLayout(self.layout)


def start(plugins):
    app = QtWidgets.QApplication([])
    app.setStyle('Fusion')

    window = App(plugins)

    window.show()
    sys.exit(app.exec_())
