from QtGUI import Ui_MainWindow
from Client import Client
from flowlayout import FlowLayout
from PyQt5 import QtWidgets, QtCore


class TrackerWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.client = Client()
        self.refresh()

        self.ui.refresh_button.clicked.connect(self.refresh)

    def refresh(self):
        self.client.update()
        num1 = self.client.get_num_champs(True)
        num2 = self.client.get_ip_needed("max", True)
        self.ui.num_champs_owned_value_label.setText(f'{num1:,}')
        self.ui.max_blue_essence_needed_value_label.setText(f'{num2:,}')


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = TrackerWindow()
    window.show()
    sys.exit(app.exec_())
