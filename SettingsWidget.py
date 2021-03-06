# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SettingsWidget.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_settings_widget(object):
    def setupUi(self, settings_widget):
        settings_widget.setObjectName("settings_widget")
        settings_widget.resize(313, 154)
        self.settings_widget_formLayout = QtWidgets.QFormLayout(settings_widget)
        self.settings_widget_formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.settings_widget_formLayout.setObjectName("settings_widget_formLayout")
        self.settings_widget_primary_sort_label = QtWidgets.QLabel(settings_widget)
        self.settings_widget_primary_sort_label.setObjectName("settings_widget_primary_sort_label")
        self.settings_widget_formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.settings_widget_primary_sort_label)
        self.settings_widget_primary_sort_dropdown = QtWidgets.QComboBox(settings_widget)
        self.settings_widget_primary_sort_dropdown.setEditable(False)
        self.settings_widget_primary_sort_dropdown.setObjectName("settings_widget_primary_sort_dropdown")
        self.settings_widget_primary_sort_dropdown.addItem("")
        self.settings_widget_primary_sort_dropdown.addItem("")
        self.settings_widget_primary_sort_dropdown.addItem("")
        self.settings_widget_primary_sort_dropdown.addItem("")
        self.settings_widget_primary_sort_dropdown.addItem("")
        self.settings_widget_formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.settings_widget_primary_sort_dropdown)
        self.settings_widget_secondary_sort_label = QtWidgets.QLabel(settings_widget)
        self.settings_widget_secondary_sort_label.setObjectName("settings_widget_secondary_sort_label")
        self.settings_widget_formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.settings_widget_secondary_sort_label)
        self.settings_widget_secondary_sort_dropdown = QtWidgets.QComboBox(settings_widget)
        self.settings_widget_secondary_sort_dropdown.setEditable(False)
        self.settings_widget_secondary_sort_dropdown.setObjectName("settings_widget_secondary_sort_dropdown")
        self.settings_widget_secondary_sort_dropdown.addItem("")
        self.settings_widget_secondary_sort_dropdown.addItem("")
        self.settings_widget_secondary_sort_dropdown.addItem("")
        self.settings_widget_secondary_sort_dropdown.addItem("")
        self.settings_widget_secondary_sort_dropdown.addItem("")
        self.settings_widget_formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.settings_widget_secondary_sort_dropdown)
        self.settings_widget_show_unowned_checkbox = QtWidgets.QCheckBox(settings_widget)
        self.settings_widget_show_unowned_checkbox.setObjectName("settings_widget_show_unowned_checkbox")
        self.settings_widget_formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.settings_widget_show_unowned_checkbox)
        self.settings_widget_last_refresh_label = QtWidgets.QLabel(settings_widget)
        self.settings_widget_last_refresh_label.setObjectName("settings_widget_last_refresh_label")
        self.settings_widget_formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.settings_widget_last_refresh_label)
        self.settings_widget_refresh_button = QtWidgets.QPushButton(settings_widget)
        self.settings_widget_refresh_button.setMaximumSize(QtCore.QSize(50, 16777215))
        self.settings_widget_refresh_button.setCheckable(False)
        self.settings_widget_refresh_button.setObjectName("settings_widget_refresh_button")
        self.settings_widget_formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.settings_widget_refresh_button)
        self.settings_widget_num_champs_owned_label = QtWidgets.QLabel(settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.settings_widget_num_champs_owned_label.sizePolicy().hasHeightForWidth())
        self.settings_widget_num_champs_owned_label.setSizePolicy(sizePolicy)
        self.settings_widget_num_champs_owned_label.setObjectName("settings_widget_num_champs_owned_label")
        self.settings_widget_formLayout.setWidget(4, QtWidgets.QFormLayout.SpanningRole, self.settings_widget_num_champs_owned_label)
        self.settings_widget_max_blue_essence_needed_label = QtWidgets.QLabel(settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.settings_widget_max_blue_essence_needed_label.sizePolicy().hasHeightForWidth())
        self.settings_widget_max_blue_essence_needed_label.setSizePolicy(sizePolicy)
        self.settings_widget_max_blue_essence_needed_label.setObjectName("settings_widget_max_blue_essence_needed_label")
        self.settings_widget_formLayout.setWidget(5, QtWidgets.QFormLayout.SpanningRole, self.settings_widget_max_blue_essence_needed_label)

        self.retranslateUi(settings_widget)
        self.settings_widget_primary_sort_dropdown.setCurrentIndex(0)
        self.settings_widget_secondary_sort_dropdown.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(settings_widget)

    def retranslateUi(self, settings_widget):
        _translate = QtCore.QCoreApplication.translate
        settings_widget.setWindowTitle(_translate("settings_widget", "Form"))
        self.settings_widget_primary_sort_label.setText(_translate("settings_widget", "Primary Sort:"))
        self.settings_widget_primary_sort_dropdown.setItemText(0, _translate("settings_widget", "Alphabetical"))
        self.settings_widget_primary_sort_dropdown.setItemText(1, _translate("settings_widget", "Mastery"))
        self.settings_widget_primary_sort_dropdown.setItemText(2, _translate("settings_widget", "Cost"))
        self.settings_widget_primary_sort_dropdown.setItemText(3, _translate("settings_widget", "Release Date"))
        self.settings_widget_primary_sort_dropdown.setItemText(4, _translate("settings_widget", "Rarity"))
        self.settings_widget_secondary_sort_label.setText(_translate("settings_widget", "Secondary Sort"))
        self.settings_widget_secondary_sort_dropdown.setItemText(0, _translate("settings_widget", "Alphabetical"))
        self.settings_widget_secondary_sort_dropdown.setItemText(1, _translate("settings_widget", "Mastery"))
        self.settings_widget_secondary_sort_dropdown.setItemText(2, _translate("settings_widget", "Cost"))
        self.settings_widget_secondary_sort_dropdown.setItemText(3, _translate("settings_widget", "Release Date"))
        self.settings_widget_secondary_sort_dropdown.setItemText(4, _translate("settings_widget", "Rarity"))
        self.settings_widget_show_unowned_checkbox.setText(_translate("settings_widget", "Show Unowned"))
        self.settings_widget_last_refresh_label.setText(_translate("settings_widget", "Last Refresh: Never"))
        self.settings_widget_refresh_button.setStyleSheet(_translate("settings_widget", "0"))
        self.settings_widget_refresh_button.setText(_translate("settings_widget", "Refresh"))
        self.settings_widget_num_champs_owned_label.setText(_translate("settings_widget", "Number of Champions Owned:"))
        self.settings_widget_max_blue_essence_needed_label.setText(_translate("settings_widget", "Maximum Blue Essence Needed:"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    settings_widget = QtWidgets.QWidget()
    ui = Ui_settings_widget()
    ui.setupUi(settings_widget)
    settings_widget.show()
    sys.exit(app.exec_())
