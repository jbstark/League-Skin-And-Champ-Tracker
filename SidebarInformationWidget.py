# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SidebarInformationWidget.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_sidebar_tab_info_stacked_widget(object):
    def setupUi(self, sidebar_tab_info_stacked_widget):
        sidebar_tab_info_stacked_widget.setObjectName("sidebar_tab_info_stacked_widget")
        sidebar_tab_info_stacked_widget.resize(430, 189)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(sidebar_tab_info_stacked_widget.sizePolicy().hasHeightForWidth())
        sidebar_tab_info_stacked_widget.setSizePolicy(sizePolicy)
        sidebar_tab_info_stacked_widget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.champs_stacked_widget_page = QtWidgets.QWidget()
        self.champs_stacked_widget_page.setObjectName("champs_stacked_widget_page")
        sidebar_tab_info_stacked_widget.addWidget(self.champs_stacked_widget_page)
        self.skins_stacked_widget_page = QtWidgets.QWidget()
        self.skins_stacked_widget_page.setObjectName("skins_stacked_widget_page")
        sidebar_tab_info_stacked_widget.addWidget(self.skins_stacked_widget_page)
        self.current_event_stacked_widget_page = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.current_event_stacked_widget_page.sizePolicy().hasHeightForWidth())
        self.current_event_stacked_widget_page.setSizePolicy(sizePolicy)
        self.current_event_stacked_widget_page.setObjectName("current_event_stacked_widget_page")
        self.current_event_stacked_widget_page_verticalLayout = QtWidgets.QVBoxLayout(self.current_event_stacked_widget_page)
        self.current_event_stacked_widget_page_verticalLayout.setObjectName("current_event_stacked_widget_page_verticalLayout")
        self.target_tokens_horizontalLayout = QtWidgets.QHBoxLayout()
        self.target_tokens_horizontalLayout.setObjectName("target_tokens_horizontalLayout")
        self.target_tokens_label = QtWidgets.QLabel(self.current_event_stacked_widget_page)
        self.target_tokens_label.setObjectName("target_tokens_label")
        self.target_tokens_horizontalLayout.addWidget(self.target_tokens_label)
        self.target_tokens_lineEdit = QtWidgets.QLineEdit(self.current_event_stacked_widget_page)
        self.target_tokens_lineEdit.setObjectName("target_tokens_lineEdit")
        self.target_tokens_horizontalLayout.addWidget(self.target_tokens_lineEdit)
        self.current_event_stacked_widget_page_verticalLayout.addLayout(self.target_tokens_horizontalLayout)
        self.current_tokens_label = QtWidgets.QLabel(self.current_event_stacked_widget_page)
        self.current_tokens_label.setObjectName("current_tokens_label")
        self.current_event_stacked_widget_page_verticalLayout.addWidget(self.current_tokens_label)
        self.tokens_per_day_label = QtWidgets.QLabel(self.current_event_stacked_widget_page)
        self.tokens_per_day_label.setObjectName("tokens_per_day_label")
        self.current_event_stacked_widget_page_verticalLayout.addWidget(self.tokens_per_day_label)
        sidebar_tab_info_stacked_widget.addWidget(self.current_event_stacked_widget_page)
        self.previous_event_stacked_widget_page = QtWidgets.QWidget()
        self.previous_event_stacked_widget_page.setObjectName("previous_event_stacked_widget_page")
        self.previous_event_stacked_widget_page_verticalLayout = QtWidgets.QVBoxLayout(self.previous_event_stacked_widget_page)
        self.previous_event_stacked_widget_page_verticalLayout.setObjectName("previous_event_stacked_widget_page_verticalLayout")
        self.previous_event_tokens_label = QtWidgets.QLabel(self.previous_event_stacked_widget_page)
        self.previous_event_tokens_label.setObjectName("previous_event_tokens_label")
        self.previous_event_stacked_widget_page_verticalLayout.addWidget(self.previous_event_tokens_label)
        sidebar_tab_info_stacked_widget.addWidget(self.previous_event_stacked_widget_page)

        self.retranslateUi(sidebar_tab_info_stacked_widget)
        sidebar_tab_info_stacked_widget.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(sidebar_tab_info_stacked_widget)

    def retranslateUi(self, sidebar_tab_info_stacked_widget):
        _translate = QtCore.QCoreApplication.translate
        sidebar_tab_info_stacked_widget.setWindowTitle(_translate("sidebar_tab_info_stacked_widget", "StackedWidget"))
        self.target_tokens_label.setText(_translate("sidebar_tab_info_stacked_widget", "TextLabel"))
        self.current_tokens_label.setText(_translate("sidebar_tab_info_stacked_widget", "TextLabel"))
        self.tokens_per_day_label.setText(_translate("sidebar_tab_info_stacked_widget", "TextLabel"))
        self.previous_event_tokens_label.setText(_translate("sidebar_tab_info_stacked_widget", "TextLabel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    sidebar_tab_info_stacked_widget = QtWidgets.QStackedWidget()
    ui = Ui_sidebar_tab_info_stacked_widget()
    ui.setupUi(sidebar_tab_info_stacked_widget)
    sidebar_tab_info_stacked_widget.show()
    sys.exit(app.exec_())
