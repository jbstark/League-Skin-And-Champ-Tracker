from QtGUI import Ui_MainWindow
from Client import Client
from flowlayout import FlowLayout
from PyQt5 import QtWidgets, QtCore, QtGui
from datetime import datetime
from PyQt5 import QtTest


class CurrentEventDetailsWidget(QtWidgets.QWidget):
    def __init__(self, client, parent=None, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        
        self.setObjectName("current_event_details_widget")
        self.setMaximumSize(300, 300)
        
        self.current_event_widget_vertical_layout = QtWidgets.QVBoxLayout(self)
        self.current_event_widget_vertical_layout.setObjectName("current_event_widget_vertical_layout")
        
        self.token_target_frame = QtWidgets.QFrame(self)
        self.token_target_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.token_target_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.token_target_frame.setObjectName("token_target_frame")
        
        self.token_target_frame_horizontal_layout = QtWidgets.QHBoxLayout(self.token_target_frame)
        self.token_target_frame_horizontal_layout.setObjectName("token_target_frame_horizontal_layout")
        self.token_target_frame_horizontal_layout.setContentsMargins(0, 9, 9, 9)
        
        self.token_target_frame_label = QtWidgets.QLabel(self.token_target_frame)
        self.token_target_frame_label.setObjectName("token_target_frame_label")
        self.token_target_frame_horizontal_layout.addWidget(self.token_target_frame_label)
        
        self.token_target_frame_input_lineedit = QtWidgets.QLineEdit(self.token_target_frame)
        self.token_target_frame_input_lineedit.setObjectName("token_target_frame_input_lineedit")
        self.token_target_frame_input_lineedit.setValidator(
            QtGui.QIntValidator(0, (2**31)-1, self.token_target_frame_input_lineedit.parent()))
        self.token_target_frame_horizontal_layout.addWidget(self.token_target_frame_input_lineedit)
        
        self.current_event_widget_vertical_layout.addWidget(self.token_target_frame)
        
        self.current_event_current_tokens_label = QtWidgets.QLabel(self)
        self.current_event_current_tokens_label.setObjectName("current_event_current_tokens_label")
        self.current_event_widget_vertical_layout.addWidget(self.current_event_current_tokens_label)
        
        self.current_event_target_tokens_per_day_label = QtWidgets.QLabel(self)
        self.current_event_target_tokens_per_day_label.setObjectName("current_event_target_tokens_per_day_label")
        self.current_event_widget_vertical_layout.addWidget(self.current_event_target_tokens_per_day_label)
        
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("current_event_details_widget", "Form"))
        self.token_target_frame_label.setText(_translate("current_event_details_widget", "Enter target tokens:"))
        self.current_event_current_tokens_label.setText(_translate("current_event_details_widget",
                                                                   f"Current tokens: {client.get_current_tokens()}"))
        self.current_event_target_tokens_per_day_label.setText(
            _translate("current_event_details_widget", "Tokens needed per day: "))
        
        QtCore.QMetaObject.connectSlotsByName(self)
        
        self.token_target_frame_input_lineedit.textEdited.connect(lambda: self.text_edited(client))
    
    def text_edited(self, client):
        new_text = self.token_target_frame_input_lineedit.text()
        try:
            self.current_event_target_tokens_per_day_label.setText(
                f"Tokens needed per day: {client.get_tokens_per_day(int(new_text))}")
        except ValueError:
            self.current_event_target_tokens_per_day_label.setText("Tokens needed per day: ")


class IconWidget(QtWidgets.QFrame):
    def __init__(self, name="", api_call_path="", cost=0, client=None, width=160, height=200, parent=None, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
    
        self.setObjectName(f"icon_frame_{name}")
        self.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))  # Indicates that the widget is clickable
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setMinimumSize(width, height)
        self.setMaximumSize(width, height)
    
        # Creates layout for the main widget
        self.icon_frame_qvboxlayout = QtWidgets.QVBoxLayout(self)
        self.icon_frame_qvboxlayout.setObjectName(f"icon_frame_{name}_qvboxlayout")
        
        # Creates and sets up the label to contain the widget's name text, and adds it to the main widget
        self.name_label = QtWidgets.QLabel(self)
        # Make the text label small
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.name_label.sizePolicy().hasHeightForWidth())
        self.name_label.setSizePolicy(sizePolicy)
        self.name_label.setAlignment(QtCore.Qt.AlignCenter)
        self.name_label.setObjectName(f"{name}_name_label")
        self.name_label.setWordWrap(True)
        self.name_label.setToolTip(name)  # Hover text is the full text
        self.name_label.setText(name)
        self.icon_frame_qvboxlayout.addWidget(self.name_label)
    
        # Creates and sets up the label to contain the widget's image
        self.image_label = QtWidgets.QLabel(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)  # Makes the image as large as possible
        sizePolicy.setHeightForWidth(self.image_label.sizePolicy().hasHeightForWidth())
        self.image_label.setSizePolicy(sizePolicy)
    
        # Loads the image data from the api, adds it to the label, and adds the label to the main widget
        image = QtGui.QImage()
        image.loadFromData(client.call_api_image(api_call_path).content)  # load image data from api
        image_pixmap = QtGui.QPixmap()
        image_pixmap = image_pixmap.fromImage(image).scaled(width - 20,
                                                            height - 20 - (height - width))  # set image size
        self.image_label.setPixmap(image_pixmap)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setObjectName(f"{name}_image_label")
        self.icon_frame_qvboxlayout.addWidget(self.image_label)

        # Creates and sets up the label to contain the widget's name text, and adds it to the main widget
        self.cost_label = QtWidgets.QLabel(self)
        # Make the text label small
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cost_label.sizePolicy().hasHeightForWidth())
        self.cost_label.setSizePolicy(sizePolicy)
        self.cost_label.setAlignment(QtCore.Qt.AlignCenter)
        self.cost_label.setObjectName(f"{name}_cost_label")
        self.cost_label.setWordWrap(True)
        if isinstance(cost, int):
            self.cost_label.setText(f"{cost} tokens")
        else:
            self.cost_label.setText(f"{cost}")
        self.icon_frame_qvboxlayout.addWidget(self.cost_label)
    
        # Boilerplate code generated by pyuic5
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("icon_frame", "Frame"))
        self.image_label.setText(_translate("icon_frame", ""))
        # self.name_label.setText(
        #    _translate("icon_frame", self.name_label.fontMetrics().elidedText(name, QtCore.Qt.ElideRight, 110)))
        QtCore.QMetaObject.connectSlotsByName(self)


def create_client_refresh_messageBox(firstOpen, parent=None):
    """
    Creates a QMessageBox popup window allowing the user to either close the program or try to find the client process.

    :param firstOpen:
    :param parent: Qt object containing the message box.
    :return: A QMessageBox window object with a message and 'Retry' and 'Close' buttons.
    """
    if firstOpen:
        text = "League of Legends client is not running. Check again?"
    else:
        text = "League of Legends has been quit. Please reopen and check again."
    client_refresh_messageBox = QtWidgets.QMessageBox(parent)
    client_refresh_messageBox.setIcon(QtWidgets.QMessageBox.Warning)
    client_refresh_messageBox.setText(text)
    client_refresh_messageBox.setWindowTitle("Client Not Running")
    client_refresh_messageBox.setStandardButtons(QtWidgets.QMessageBox.Retry | QtWidgets.QMessageBox.Close)
    client_refresh_messageBox.setDefaultButton(QtWidgets.QMessageBox.Retry)
    client_refresh_messageBox.setEscapeButton(QtWidgets.QMessageBox.Close)
    client_refresh_messageBox.buttonClicked.connect(client_refresh_button_clicked)
    return client_refresh_messageBox


def client_refresh_button_clicked(i):
    """
    Defines the action to be taken when the user clicks a button in the client refresh message box window.

    :param i: Contains information about the button pressed.
    """
    if i.text() == "Close":
        sys.exit()


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
        self.current_event_widget = None
    
        self.client = Client()
        while not self.client.clientRunning:
            create_client_refresh_messageBox(True, self.ui.centralwidget).exec_()
            self.client.check_client_running()
        self.refresh()
    
        self.ui.tab_widget.currentChanged.connect(self.new_tab_selected)
        self.new_tab_selected()
        self.populate_current_event_tab()
    
    def new_tab_selected(self):
        if self.ui.tab_widget.tabText(self.ui.tab_widget.currentIndex()) == "Current Event":
            self.current_event_widget = self.current_event_sidebar()
            self.ui.left_panel_frame_vertical_layout.addWidget(self.current_event_widget,
                                                               alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        else:
            if not (self.current_event_widget is None):
                self.ui.left_panel_frame_vertical_layout.removeWidget(self.current_event_widget)
                self.current_event_widget.deleteLater()
                self.current_event_widget = None
    
    def current_event_sidebar(self):
        return CurrentEventDetailsWidget(self.client, parent=self.ui.left_panel_frame)
    
    def populate_current_event_tab(self):
        """Adds all purchasable item widgets to the current event tab."""
        event_shop = self.client.get_event_shop()
        for item in event_shop:
            cost = item[2]
            if item[3]:
                cost = "Owned"
            self.ui.current_event_tab_scroll_area_widget_contents_layout.addWidget(
                IconWidget(
                    item[0], item[1], cost, self.client, parent=self.ui.current_event_tab_scroll_area_widget_contents))
    
    def setup_champs_tab_layout(self):
        """Creates flow layout for the champs tab."""
        self.ui.champs_tab_scroll_area_widget_contents_layout = FlowLayout(
            self.ui.champs_tab_scroll_area_widget_contents)
        self.ui.champs_tab_scroll_area_widget_contents_layout.setObjectName(
            "champs_tab_scroll_area_widget_contents_layout")
    
    def setup_current_event_tab_layout(self):
        """Creates flow layout for the current event tab."""
        self.ui.current_event_tab_scroll_area_widget_contents_layout = FlowLayout(
            self.ui.current_event_tab_scroll_area_widget_contents)
        self.ui.current_event_tab_scroll_area_widget_contents_layout.setObjectName(
            "current_event_tab_scroll_area_widget_contents_layout")
    
    def setup_refresh_button(self):
        """Configures the refresh button."""
        self.ui.refresh_button.clicked.connect(self.refresh)
    
    def setup_refresh_label_timer(self):
        """Configures and starts the refresh label timer."""
        self.ui.refresh_label_timer = QtCore.QTimer(self.ui.last_refresh_label)
        self.ui.refresh_label_timer.setObjectName("refresh_label_timer")
        self.ui.refresh_label_timer.setInterval(30000)  # 60 seconds
        self.ui.refresh_label_timer.setSingleShot(False)  # repeat timer on timeout
        self.ui.refresh_label_timer.timeout.connect(self.reset_refresh_label)  # call reset_refresh_label on timeout
        self.ui.refresh_label_timer.start()
    
    def refresh(self):
        """Updates client data and resets its text."""
        try:
            self.client.update()
        except TypeError:
            # The client has been closed
            closing = True
            self.client.clientRunning = False
            self.client.lockfileFound = False
            
            # While the client is still closing, look for the lockfile
            while closing:
                # Wait one second before trying to open the file again
                QtTest.QTest.qWait(1000)
                try:
                    with open(self.client.currentDirectory, 'r'):
                        pass
                # Lockfile is gone, client is fully closed
                except FileNotFoundError:
                    closing = False
                    print("Client fully closed")
            
            # While the client is not running, ask if they user wants to refresh
            while not self.client.clientRunning:
                create_client_refresh_messageBox(False, self.ui.centralwidget).exec_()
                self.client.check_client_running()
            # Client is now running and can be refreshed
            self.refresh()
        
        self.ui.num_champs_owned_value_label.setText(self.client.get_num_champs(True))
        self.ui.max_blue_essence_needed_value_label.setText(self.client.get_ip_needed("max", True, True))
        
        self.last_refresh_time = datetime.now()
        self.reset_refresh_label()
    
    def reset_refresh_label(self):
        """Updates the refresh label with correct elapsed time."""
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
