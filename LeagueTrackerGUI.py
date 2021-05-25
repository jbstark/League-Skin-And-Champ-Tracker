from QtGUI import Ui_MainWindow
from Client import Client
from flowlayout import FlowLayout
from PyQt5 import QtWidgets, QtCore
from datetime import datetime


class TrackerWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setup_refresh_label_timer()
        self.setup_refresh_button()

        self.last_refresh_time = None

        self.client = Client()
        self.refresh()

    def setup_refresh_button(self):
        self.ui.refresh_button.clicked.connect(self.refresh)

    def setup_refresh_label_timer(self):
        self.ui.refresh_label_timer = QtCore.QTimer(self.ui.last_refresh_label)
        self.ui.refresh_label_timer.setObjectName("refresh_label_timer")
        self.ui.refresh_label_timer.setInterval(60000)
        self.ui.refresh_label_timer.setSingleShot(False)
        self.ui.refresh_label_timer.timeout.connect(self.reset_refresh_label)
        self.ui.refresh_label_timer.start()

    def refresh(self):
        self.client.update()
        self.ui.num_champs_owned_value_label.setText(self.client.get_num_champs(True))
        self.ui.max_blue_essence_needed_value_label.setText(self.client.get_ip_needed("max", True))

        self.last_refresh_time = datetime.now()
        self.reset_refresh_label()

    def reset_refresh_label(self):
        elapsed_time = datetime.now() - self.last_refresh_time
        elapsed_seconds = elapsed_time.total_seconds()
        elapsed_minutes = int(elapsed_seconds / 60)

        if elapsed_minutes < 1:
            self.ui.last_refresh_label.setText("Last Refresh: < 1 minute ago")
        elif elapsed_minutes == 1:
            self.ui.last_refresh_label.setText("Last Refresh: 1 minute ago")
        elif elapsed_minutes > 60:
            self.ui.last_refresh_label.setText("Last Refresh: > 1 hour ago")
        else:
            self.ui.last_refresh_label.setText(f"Last Refresh: {elapsed_minutes} minutes ago")


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = TrackerWindow()
    window.show()
    sys.exit(app.exec_())
