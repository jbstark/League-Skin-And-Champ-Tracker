from QtGUI import Ui_MainWindow
from Client import Client
from flowlayout import FlowLayout
from PyQt5 import QtWidgets, QtCore, QtGui
from datetime import datetime


def create_new_icon_widget(name, api_call_path, client, width=160, height=200, parent=None):
    image_data = client.call_api_image(api_call_path).content
    image = QtGui.QImage()
    image.loadFromData(image_data)

    icon_frame = QtWidgets.QFrame(parent=parent)
    icon_frame.setObjectName("icon_frame")
    icon_frame.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
    icon_frame.setFrameShape(QtWidgets.QFrame.Box)
    icon_frame.setMinimumSize(width, height)
    icon_frame.setMaximumSize(width, height)

    icon_frame_label = QtWidgets.QVBoxLayout(icon_frame)
    icon_frame_label.setObjectName("icon_frame_label")

    image_label = QtWidgets.QLabel(icon_frame)

    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(1)
    sizePolicy.setHeightForWidth(image_label.sizePolicy().hasHeightForWidth())
    image_label.setSizePolicy(sizePolicy)

    image_pixmap = QtGui.QPixmap()
    image_pixmap = image_pixmap.fromImage(image).scaled(width-20, height-20-(height-width))
    image_label.setPixmap(image_pixmap)
    image_label.setAlignment(QtCore.Qt.AlignCenter)
    image_label.setObjectName("image_label")
    icon_frame_label.addWidget(image_label)

    name_label = QtWidgets.QLabel(icon_frame)

    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(name_label.sizePolicy().hasHeightForWidth())
    name_label.setSizePolicy(sizePolicy)

    name_label.setAlignment(QtCore.Qt.AlignCenter)
    name_label.setObjectName("name_label")
    name_label.setWordWrap(True)
    name_label.setText(name_label.fontMetrics().elidedText(name, QtCore.Qt.ElideRight, 100))
    name_label.setToolTip(name)
    icon_frame_label.addWidget(name_label)

    _translate = QtCore.QCoreApplication.translate
    icon_frame.setWindowTitle(_translate("icon_frame", "Frame"))
    image_label.setText(_translate("icon_frame", ""))
    name_label.setText(_translate("icon_frame", name))

    QtCore.QMetaObject.connectSlotsByName(icon_frame)

    return icon_frame


class TrackerWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        """
        Initialises the main window for the application. Inherits from QMainWindow.
        :param args: Non-Keyword Arguments
        :param kwargs: Keyword Arguments
        """
        super().__init__(*args, **kwargs)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setup_refresh_label_timer()
        self.setup_refresh_button()
        self.setup_champs_tab_layout()
        self.setup_current_event_tab_layout()

        self.last_refresh_time = None

        self.client = Client()
        self.refresh()

        self.populate_current_event_tab()

    def populate_current_event_tab(self):
        event_shop = self.client.get_event_shop()
        for item in event_shop:
            self.ui.current_event_tab_scroll_area_widget_contents_layout.addWidget(
                create_new_icon_widget(
                    item[0], item[1], self.client, parent=self.ui.current_event_tab_scroll_area_widget_contents))

    def setup_champs_tab_layout(self):
        self.ui.champs_tab_scroll_area_widget_contents_layout = FlowLayout(
            self.ui.champs_tab_scroll_area_widget_contents)
        self.ui.champs_tab_scroll_area_widget_contents_layout.setObjectName(
            "champs_tab_scroll_area_widget_contents_layout")
        
    def setup_current_event_tab_layout(self):
        self.ui.current_event_tab_scroll_area_widget_contents_layout = FlowLayout(
            self.ui.current_event_tab_scroll_area_widget_contents)
        self.ui.current_event_tab_scroll_area_widget_contents_layout.setObjectName(
            "current_event_tab_scroll_area_widget_contents_layout")

    def setup_refresh_button(self):
        """
        Configures the refresh button
        """
        self.ui.refresh_button.clicked.connect(self.refresh)

    def setup_refresh_label_timer(self):
        """
        Configures and starts the refresh label timer
        """
        self.ui.refresh_label_timer = QtCore.QTimer(self.ui.last_refresh_label)
        self.ui.refresh_label_timer.setObjectName("refresh_label_timer")
        self.ui.refresh_label_timer.setInterval(30000)  # 60 seconds
        self.ui.refresh_label_timer.setSingleShot(False)  # repeat timer on timeout
        self.ui.refresh_label_timer.timeout.connect(self.reset_refresh_label)  # call reset_refresh_label on timeout
        self.ui.refresh_label_timer.start()

    def refresh(self):
        """
        Updates client data and resets its text
        """
        self.client.update()
        self.ui.num_champs_owned_value_label.setText(self.client.get_num_champs(True))
        self.ui.max_blue_essence_needed_value_label.setText(self.client.get_ip_needed("max", True, True))

        self.last_refresh_time = datetime.now()
        self.reset_refresh_label()

    def reset_refresh_label(self):
        """
        Updates the refresh label with correct elapsed time
        """
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
