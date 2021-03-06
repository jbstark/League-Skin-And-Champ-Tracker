import SidebarInformationWidget
from QtGUI import Ui_MainWindow
from ShoppingCart import Ui_shopping_cart_widget
from CartItem import Ui_CartItem
from SidebarInformationWidget import Ui_sidebar_tab_info_stacked_widget
from SettingsWidget import Ui_settings_widget
from Client import Client
from flowlayout import FlowLayout
from PyQt5 import QtWidgets, QtCore, QtGui
from datetime import datetime
from PyQt5 import QtTest
from enum import IntEnum, unique
import logging


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


class SidebarInfoWidget(QtWidgets.QStackedWidget):
    def __init__(self, client, parent=None, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        
        self.ui = Ui_sidebar_tab_info_stacked_widget()
        self.ui.setupUi(self)
        
        self.client = client
        
        self.setObjectName("tab_details_widget")
        self.ui.current_event_target_tokens_lineEdit.setValidator(
            QtGui.QIntValidator(0, (2 ** 31) - 1, self.ui.current_event_target_tokens_lineEdit.parent()))
        
        self.ui.current_event_current_tokens_label.setText(f"Current tokens: {client.get_current_tokens(False)}")
        self.ui.previous_event_current_tokens_label.setText(f"Current tokens: {client.get_current_tokens(True)}")
        
        self.ui.current_event_target_tokens_lineEdit.textEdited.connect(self.current_event_target_tokens_text_edited)
    
    def current_event_target_tokens_text_edited(self):
        new_text = self.ui.current_event_target_tokens_lineEdit.text()
        try:
            self.ui.current_event_tokens_per_day_label.setText(
                f"Tokens needed per day: {self.client.get_tokens_per_day(int(new_text))}")
        except ValueError:
            self.ui.current_event_tokens_per_day_label.setText("Tokens needed per day: ")
    
    @unique
    class TabIndex(IntEnum):
        CHAMPIONS = 0
        SKINS = 1
        CURRENT_EVENT = 2
        PREVIOUS_EVENT = 3
        

class IconWidget(QtWidgets.QFrame):
    clicked = QtCore.pyqtSignal(str, int)
    
    def __init__(self, name="", api_call_path="", cost=0, client=None, width=200, height=250, parent=None, *args,
                 **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
    
        self.setObjectName(f"icon_frame_{name}")
        self.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))  # Indicates that the widget is clickable
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
            if cost == 1:
                self.cost_label.setText(f"{cost} token")
            else:
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

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        import re
        cost = self.cost_label.text()
        cost = re.sub("[^0-9]", "", cost)
        self.clicked.emit(self.name_label.text(), int(cost))

    def enterEvent(self, a0: QtCore.QEvent) -> None:
        self.setFrameShape(QtWidgets.QFrame.Box)

    def leaveEvent(self, a0: QtCore.QEvent) -> None:
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        

class SettingsWidget(QtWidgets.QWidget):
    def __init__(self, client, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.ui = Ui_settings_widget()
        self.ui.setupUi(self)
        
        self.client = client

        self.last_refresh_time = None
        
        self.setup_refresh_button()
        self.setup_refresh_label_timer()
        self.refresh()

    def setup_refresh_button(self):
        """Configures the refresh button."""
        self.ui.settings_widget_refresh_button.clicked.connect(self.refresh)

    def setup_refresh_label_timer(self):
        """Configures and starts the refresh label timer."""
        self.ui.settings_widget_refresh_label_timer = QtCore.QTimer(self.ui.settings_widget_last_refresh_label)
        self.ui.settings_widget_refresh_label_timer.setObjectName("refresh_label_timer")
        self.ui.settings_widget_refresh_label_timer.setInterval(30000)  # 60 seconds
        self.ui.settings_widget_refresh_label_timer.setSingleShot(False)  # repeat timer on timeout
        self.ui.settings_widget_refresh_label_timer.timeout.connect(self.reset_refresh_label)  # call reset_refresh_label on timeout
        self.ui.settings_widget_refresh_label_timer.start()

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
    
        self.ui.settings_widget_num_champs_owned_label.setText(
            f"Number of Champions Owned: {self.client.get_num_champs(True)}")
        self.ui.settings_widget_max_blue_essence_needed_label.setText(
            f"Maximum Blue Essence Needed: {self.client.get_ip_needed('max', True, True)}")
    
        self.last_refresh_time = datetime.now()
        self.reset_refresh_label()

    def reset_refresh_label(self):
        """Updates the refresh label with correct elapsed time."""
        elapsed_time = datetime.now() - self.last_refresh_time
        elapsed_seconds = elapsed_time.total_seconds()
        elapsed_minutes = int(elapsed_seconds / 60)
    
        if elapsed_minutes < 1:
            self.ui.settings_widget_last_refresh_label.setText("Last Refresh: < 1 minute ago")
        elif elapsed_minutes == 1:
            self.ui.settings_widget_last_refresh_label.setText("Last Refresh: 1 minute ago")
        elif elapsed_minutes > 60:
            self.ui.settings_widget_last_refresh_label.setText("Last Refresh: > 1 hour ago")
        else:
            self.ui.settings_widget_last_refresh_label.setText(f"Last Refresh: {elapsed_minutes} minutes ago")
    

class ShoppingCart(QtWidgets.QWidget):
    class CartItem(QtWidgets.QWidget):
        delete = QtCore.pyqtSignal(str)
        amount_changed = QtCore.pyqtSignal(str)
        
        def __init__(self, item_name, cost, parent=None):
            super().__init__(parent=parent)
            
            self.ui = Ui_CartItem()
            self.ui.setupUi(self)
            
            self.name = item_name
            self.cost = cost
            self.quantity = 1
            
            self.ui.item_label.setText(f"{self.name} ({self.cost} tokens)")
            
            self.ui.item_quantity_spinBox.valueChanged.connect(self.update_quantity)
            self.ui.remove_item_button.clicked.connect(self.remove_item)
            
        def update_quantity(self):
            self.quantity = self.ui.item_quantity_spinBox.value()
            self.amount_changed.emit(self.name)
        
        def remove_item(self, name):
            self.delete.emit(self.name)
        
        def total_cost(self):
            return self.cost * self.quantity
        
    def __init__(self, parent=None):
        super().__init__()
        
        self.ui = Ui_shopping_cart_widget()
        self.ui.setupUi(self)
        
        self.items = dict()
        self.cart_total = 0
        
        self.ui.shopping_cart_scrollAreaWidgetContents_verticalLayout.setAlignment(QtCore.Qt.AlignTop)
        
    def add_item(self, item_name, item_cost):
        new_item = ShoppingCart.CartItem(item_name, item_cost, parent=self.ui.shopping_cart_scrollAreaWidgetContents)
        new_item.delete.connect(self.delete_item)
        new_item.amount_changed.connect(self.refresh_cart_total)
        self.ui.shopping_cart_scrollAreaWidgetContents_verticalLayout.addWidget(new_item)
        self.items[item_name] = new_item

        self.update_cost(new_item.total_cost())
        
    def delete_item(self, item_name):
        item = self.items.pop(item_name)
        self.ui.shopping_cart_scrollAreaWidgetContents_verticalLayout.removeWidget(item)
        self.update_cost(-item.total_cost())
        item.deleteLater()
        
    def contains(self, name):
        return name in self.items.keys()
    
    def update_cost(self, delta):
        self.cart_total += delta
        self.ui.cart_total_label.setText(f"Total cost: {self.cart_total}")
        
    def refresh_cart_total(self, item_name):
        total = 0
        for item in self.items.values():
            total += item.total_cost()
        self.cart_total = total
        self.ui.cart_total_label.setText(f"Total cost: {self.cart_total}")
        
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
        
        self.client = Client()
        while not self.client.clientRunning:
            create_client_refresh_messageBox(True, self.ui.centralwidget).exec_()
            self.client.check_client_running()
    
        self.setup_current_event_tab_layout()

        self.config_event_tabs()
    
        self.sidebar_info_widget = None
        self.current_event_shop_items = []
    
        self.ui.tab_widget.currentChanged.connect(self.new_tab_selected)
        self.ui.left_panel_frame_vertical_layout.addWidget(SettingsWidget(client=self.client,
                                                                          parent=self.ui.left_panel_frame))
        
        self.create_sidebar_info_widget()
        self.shopping_cart = ShoppingCart(parent=self.ui.left_panel_frame)
        self.ui.left_panel_frame_vertical_layout.addWidget(self.shopping_cart)
        self.new_tab_selected()
        self.populate_current_event_tab()
        self.populate_previous_event_tab()

    def config_event_tabs(self):
        if None not in self.client.get_event_for_tabs():
            self.ui.previous_event_tab = QtWidgets.QWidget()
            self.ui.previous_event_tab.setObjectName("previous_event_tab")
        
            self.ui.previous_event_tab_flowLayout = QtWidgets.QGridLayout(self.ui.previous_event_tab)
            self.ui.previous_event_tab_flowLayout.setObjectName("previous_event_tab")
        
            self.ui.previous_event_tab_scroll_area = QtWidgets.QScrollArea(self.ui.previous_event_tab)
            self.ui.previous_event_tab_scroll_area.setObjectName("previous_event_tab_scroll_area")
            self.ui.previous_event_tab_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
            self.ui.previous_event_tab_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            self.ui.previous_event_tab_scroll_area.setWidgetResizable(True)
        
            self.ui.previous_event_tab_scroll_area_widget_contents = QtWidgets.QWidget()
            self.ui.previous_event_tab_scroll_area_widget_contents.setObjectName(
                "previous_event_tab_scroll_area_widget_contents")
            self.ui.previous_event_tab_scroll_area.setWidget(self.ui.previous_event_tab_scroll_area_widget_contents)
            self.ui.previous_event_tab_flowLayout.addWidget(self.ui.previous_event_tab_scroll_area)
        
            self.ui.tab_widget.addTab(self.ui.previous_event_tab, f"{self.client.get_event_for_tabs()[0]} Event")
            self.ui.tab_widget.setTabText(2, f"{self.client.get_event_for_tabs()[1]} Event")
        else:
            self.ui.tab_widget.setTabText(2, f"{self.client.get_event_for_tabs()[1]} Event")

    def new_tab_selected(self):
        if self.ui.tab_widget.tabText(self.ui.tab_widget.currentIndex()) == "Champions":
            self.sidebar_info_widget.setCurrentIndex(SidebarInfoWidget.TabIndex.CHAMPIONS)
        elif self.ui.tab_widget.tabText(self.ui.tab_widget.currentIndex()) == "Skins":
            self.sidebar_info_widget.setCurrentIndex(SidebarInfoWidget.TabIndex.SKINS)
        elif self.ui.tab_widget.tabText(self.ui.tab_widget.currentIndex()) == \
                f"{self.client.get_event_for_tabs()[1]} Event":
            self.sidebar_info_widget.setCurrentIndex(SidebarInfoWidget.TabIndex.CURRENT_EVENT)
        elif self.ui.tab_widget.tabText(self.ui.tab_widget.currentIndex()) == \
                f"{self.client.get_event_for_tabs()[0]} Event":
            self.sidebar_info_widget.setCurrentIndex(SidebarInfoWidget.TabIndex.PREVIOUS_EVENT)
            
    def create_sidebar_info_widget(self):
        self.sidebar_info_widget = SidebarInfoWidget(self.client, parent=self.ui.left_panel_frame)
        self.ui.left_panel_frame_vertical_layout.addWidget(self.sidebar_info_widget)
    
    def populate_current_event_tab(self):
        """Adds all purchasable item widgets to the current event tab."""
        event_shop = self.client.get_event_shop(False)
        for item in event_shop:
            cost = item[2]
            if item[3]:
                cost = "Owned"
            elif item[2] == 0:
                cost = "Unknown"
            icon_widget = IconWidget(
                    item[0], item[1], cost, self.client, parent=self.ui.current_event_tab_scroll_area_widget_contents)
            self.current_event_shop_items.append(icon_widget)
            icon_widget.clicked.connect(self.icon_widget_clicked)
            self.ui.current_event_tab_scroll_area_widget_contents_layout.addWidget(icon_widget)
            
    def populate_previous_event_tab(self):
        """Adds all purchasable item widgets to the current event tab."""
        event_shop = self.client.get_event_shop(True)
        for item in event_shop:
            cost = item[2]
            if item[3]:
                cost = "Owned"
            elif item[2] == 0:
                cost = "Unknown"
            self.ui.previous_event_tab_scroll_area_widget_contents_layout.addWidget(
                IconWidget(
                    item[0], item[1], cost, self.client, parent=self.ui.previous_event_tab_scroll_area_widget_contents))
    
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
        
    def setup_previous_event_tab_layout(self):
        """Creates flow layout for the previous event tab."""
        self.ui.current_event_tab_scroll_area_widget_contents_layout = FlowLayout(
            self.ui.previous_event_tab_scroll_area_widget_contents)
        self.ui.current_event_tab_scroll_area_widget_contents_layout.setObjectName(
            "previous_event_tab_scroll_area_widget_contents_layout")

    def icon_widget_clicked(self, name, cost):
        if not self.shopping_cart.contains(name):
            self.shopping_cart.add_item(name, cost)
        

if __name__ == "__main__":
    import sys
    
    app = QtWidgets.QApplication(sys.argv)
    window = TrackerWindow()
    window.show()
    sys.exit(app.exec_())
