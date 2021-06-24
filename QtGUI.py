# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'QtGUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1014, 687)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.window_grid_layout = QtWidgets.QGridLayout(self.centralwidget)
        self.window_grid_layout.setObjectName("window_grid_layout")
        self.main_frame = QtWidgets.QFrame(self.centralwidget)
        self.main_frame.setStyleSheet("")
        self.main_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.main_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.main_frame.setObjectName("main_frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.main_frame)
        self.horizontalLayout.setContentsMargins(-1, -1, -1, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.left_panel_frame = QtWidgets.QFrame(self.main_frame)
        self.left_panel_frame.setMinimumSize(QtCore.QSize(0, 0))
        self.left_panel_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.left_panel_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.left_panel_frame.setObjectName("left_panel_frame")
        self.left_panel_frame_vertical_layout = QtWidgets.QVBoxLayout(self.left_panel_frame)
        self.left_panel_frame_vertical_layout.setContentsMargins(0, -1, -1, 0)
        self.left_panel_frame_vertical_layout.setObjectName("left_panel_frame_vertical_layout")
        self.settings_widget = QtWidgets.QWidget(self.left_panel_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.settings_widget.sizePolicy().hasHeightForWidth())
        self.settings_widget.setSizePolicy(sizePolicy)
        self.settings_widget.setMinimumSize(QtCore.QSize(300, 200))
        self.settings_widget.setMaximumSize(QtCore.QSize(300, 300))
        self.settings_widget.setObjectName("settings_widget")
        self.settings_vertical_layout = QtWidgets.QVBoxLayout(self.settings_widget)
        self.settings_vertical_layout.setContentsMargins(0, -1, -1, -1)
        self.settings_vertical_layout.setObjectName("settings_vertical_layout")
        self.sort_frame = QtWidgets.QFrame(self.settings_widget)
        self.sort_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.sort_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.sort_frame.setObjectName("sort_frame")
        self.sort_form_layout = QtWidgets.QFormLayout(self.sort_frame)
        self.sort_form_layout.setObjectName("sort_form_layout")
        self.primary_sort_label = QtWidgets.QLabel(self.sort_frame)
        self.primary_sort_label.setObjectName("primary_sort_label")
        self.sort_form_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.primary_sort_label)
        self.primary_sort_dropdown = QtWidgets.QComboBox(self.sort_frame)
        self.primary_sort_dropdown.setEditable(False)
        self.primary_sort_dropdown.setObjectName("primary_sort_dropdown")
        self.primary_sort_dropdown.addItem("")
        self.primary_sort_dropdown.addItem("")
        self.primary_sort_dropdown.addItem("")
        self.primary_sort_dropdown.addItem("")
        self.primary_sort_dropdown.addItem("")
        self.sort_form_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.primary_sort_dropdown)
        self.secondary_sort_label = QtWidgets.QLabel(self.sort_frame)
        self.secondary_sort_label.setObjectName("secondary_sort_label")
        self.sort_form_layout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.secondary_sort_label)
        self.secondary_sort_dropdown = QtWidgets.QComboBox(self.sort_frame)
        self.secondary_sort_dropdown.setEditable(False)
        self.secondary_sort_dropdown.setObjectName("secondary_sort_dropdown")
        self.secondary_sort_dropdown.addItem("")
        self.secondary_sort_dropdown.addItem("")
        self.secondary_sort_dropdown.addItem("")
        self.secondary_sort_dropdown.addItem("")
        self.secondary_sort_dropdown.addItem("")
        self.sort_form_layout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.secondary_sort_dropdown)
        self.show_unowned_checkbox = QtWidgets.QCheckBox(self.sort_frame)
        self.show_unowned_checkbox.setObjectName("show_unowned_checkbox")
        self.sort_form_layout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.show_unowned_checkbox)
        self.last_refresh_label = QtWidgets.QLabel(self.sort_frame)
        self.last_refresh_label.setObjectName("last_refresh_label")
        self.sort_form_layout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.last_refresh_label)
        self.refresh_button = QtWidgets.QPushButton(self.sort_frame)
        self.refresh_button.setMaximumSize(QtCore.QSize(50, 16777215))
        self.refresh_button.setCheckable(False)
        self.refresh_button.setObjectName("refresh_button")
        self.sort_form_layout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.refresh_button)
        self.settings_vertical_layout.addWidget(self.sort_frame)
        self.stats_widget = QtWidgets.QWidget(self.settings_widget)
        self.stats_widget.setMinimumSize(QtCore.QSize(0, 20))
        self.stats_widget.setObjectName("stats_widget")
        self.stats_widget_layout = QtWidgets.QFormLayout(self.stats_widget)
        self.stats_widget_layout.setObjectName("stats_widget_layout")
        self.num_champs_owned_label = QtWidgets.QLabel(self.stats_widget)
        self.num_champs_owned_label.setObjectName("num_champs_owned_label")
        self.stats_widget_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.num_champs_owned_label)
        self.max_blue_essence_needed_label = QtWidgets.QLabel(self.stats_widget)
        self.max_blue_essence_needed_label.setObjectName("max_blue_essence_needed_label")
        self.stats_widget_layout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.max_blue_essence_needed_label)
        self.max_blue_essence_needed_value_label = QtWidgets.QLabel(self.stats_widget)
        self.max_blue_essence_needed_value_label.setObjectName("max_blue_essence_needed_value_label")
        self.stats_widget_layout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.max_blue_essence_needed_value_label)
        self.num_champs_owned_value_label = QtWidgets.QLabel(self.stats_widget)
        self.num_champs_owned_value_label.setObjectName("num_champs_owned_value_label")
        self.stats_widget_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.num_champs_owned_value_label)
        self.settings_vertical_layout.addWidget(self.stats_widget)
        self.left_panel_frame_vertical_layout.addWidget(self.settings_widget, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.horizontalLayout.addWidget(self.left_panel_frame, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.tab_widget = QtWidgets.QTabWidget(self.main_frame)
        self.tab_widget.setMinimumSize(QtCore.QSize(400, 400))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.tab_widget.setFont(font)
        self.tab_widget.setObjectName("tab_widget")
        self.champs_tab = QtWidgets.QWidget()
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.champs_tab.setFont(font)
        self.champs_tab.setToolTip("")
        self.champs_tab.setObjectName("champs_tab")
        self.champs_tab_grid_layout = QtWidgets.QGridLayout(self.champs_tab)
        self.champs_tab_grid_layout.setObjectName("champs_tab_grid_layout")
        self.champs_tab_scroll_area = QtWidgets.QScrollArea(self.champs_tab)
        self.champs_tab_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.champs_tab_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.champs_tab_scroll_area.setWidgetResizable(True)
        self.champs_tab_scroll_area.setObjectName("champs_tab_scroll_area")
        self.champs_tab_scroll_area_widget_contents = QtWidgets.QWidget()
        self.champs_tab_scroll_area_widget_contents.setGeometry(QtCore.QRect(0, 0, 633, 571))
        self.champs_tab_scroll_area_widget_contents.setObjectName("champs_tab_scroll_area_widget_contents")
        self.champs_tab_scroll_area.setWidget(self.champs_tab_scroll_area_widget_contents)
        self.champs_tab_grid_layout.addWidget(self.champs_tab_scroll_area, 0, 0, 1, 1)
        self.tab_widget.addTab(self.champs_tab, "")
        self.skins_tab = QtWidgets.QWidget()
        self.skins_tab.setObjectName("skins_tab")
        self.skins_tab_grid_layout = QtWidgets.QGridLayout(self.skins_tab)
        self.skins_tab_grid_layout.setObjectName("skins_tab_grid_layout")
        self.skins_tab_scroll_area = QtWidgets.QScrollArea(self.skins_tab)
        self.skins_tab_scroll_area.setWidgetResizable(True)
        self.skins_tab_scroll_area.setObjectName("skins_tab_scroll_area")
        self.skins_tab_scroll_area_widget_contents = QtWidgets.QWidget()
        self.skins_tab_scroll_area_widget_contents.setGeometry(QtCore.QRect(0, 0, 633, 571))
        self.skins_tab_scroll_area_widget_contents.setObjectName("skins_tab_scroll_area_widget_contents")
        self.skins_tab_scroll_area.setWidget(self.skins_tab_scroll_area_widget_contents)
        self.skins_tab_grid_layout.addWidget(self.skins_tab_scroll_area, 0, 0, 1, 1)
        self.tab_widget.addTab(self.skins_tab, "")
        self.current_event_tab = QtWidgets.QWidget()
        self.current_event_tab.setObjectName("current_event_tab")
        self.current_event_tab_grid_layout = QtWidgets.QGridLayout(self.current_event_tab)
        self.current_event_tab_grid_layout.setObjectName("current_event_tab_grid_layout")
        self.current_event_tab_scroll_area = QtWidgets.QScrollArea(self.current_event_tab)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.current_event_tab_scroll_area.setFont(font)
        self.current_event_tab_scroll_area.setWidgetResizable(True)
        self.current_event_tab_scroll_area.setObjectName("current_event_tab_scroll_area")
        self.current_event_tab_scroll_area_widget_contents = QtWidgets.QWidget()
        self.current_event_tab_scroll_area_widget_contents.setGeometry(QtCore.QRect(0, 0, 633, 571))
        self.current_event_tab_scroll_area_widget_contents.setStyleSheet("")
        self.current_event_tab_scroll_area_widget_contents.setObjectName("current_event_tab_scroll_area_widget_contents")
        self.current_event_tab_scroll_area.setWidget(self.current_event_tab_scroll_area_widget_contents)
        self.current_event_tab_grid_layout.addWidget(self.current_event_tab_scroll_area, 0, 0, 1, 1)
        self.tab_widget.addTab(self.current_event_tab, "")
        self.horizontalLayout.addWidget(self.tab_widget)
        self.window_grid_layout.addWidget(self.main_frame, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1014, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.primary_sort_dropdown.setCurrentIndex(0)
        self.secondary_sort_dropdown.setCurrentIndex(0)
        self.tab_widget.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "League Tracker"))
        self.primary_sort_label.setText(_translate("MainWindow", "Primary Sort:"))
        self.primary_sort_dropdown.setItemText(0, _translate("MainWindow", "Alphabetical"))
        self.primary_sort_dropdown.setItemText(1, _translate("MainWindow", "Mastery"))
        self.primary_sort_dropdown.setItemText(2, _translate("MainWindow", "Cost"))
        self.primary_sort_dropdown.setItemText(3, _translate("MainWindow", "Release Date"))
        self.primary_sort_dropdown.setItemText(4, _translate("MainWindow", "Rarity"))
        self.secondary_sort_label.setText(_translate("MainWindow", "Secondary Sort"))
        self.secondary_sort_dropdown.setItemText(0, _translate("MainWindow", "Alphabetical"))
        self.secondary_sort_dropdown.setItemText(1, _translate("MainWindow", "Mastery"))
        self.secondary_sort_dropdown.setItemText(2, _translate("MainWindow", "Cost"))
        self.secondary_sort_dropdown.setItemText(3, _translate("MainWindow", "Release Date"))
        self.secondary_sort_dropdown.setItemText(4, _translate("MainWindow", "Rarity"))
        self.show_unowned_checkbox.setText(_translate("MainWindow", "Show Unowned"))
        self.last_refresh_label.setText(_translate("MainWindow", "Last Refresh: Never"))
        self.refresh_button.setStyleSheet(_translate("MainWindow", "0"))
        self.refresh_button.setText(_translate("MainWindow", "Refresh"))
        self.num_champs_owned_label.setText(_translate("MainWindow", "Number of Champions Owned:"))
        self.max_blue_essence_needed_label.setText(_translate("MainWindow", "Maximum Blue Essence Needed:"))
        self.max_blue_essence_needed_value_label.setText(_translate("MainWindow", "TextLabel"))
        self.num_champs_owned_value_label.setText(_translate("MainWindow", "TextLabel"))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.champs_tab), _translate("MainWindow", "Champions"))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.skins_tab), _translate("MainWindow", "Skins"))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.current_event_tab), _translate("MainWindow", "Current Event"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
