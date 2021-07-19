# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\CartItem.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CartItem(object):
    def setupUi(self, CartItem):
        CartItem.setObjectName("CartItem")
        CartItem.resize(401, 75)
        self.horizontalLayout = QtWidgets.QHBoxLayout(CartItem)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.remove_item_button = QtWidgets.QPushButton(CartItem)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.remove_item_button.sizePolicy().hasHeightForWidth())
        self.remove_item_button.setSizePolicy(sizePolicy)
        self.remove_item_button.setMinimumSize(QtCore.QSize(50, 25))
        self.remove_item_button.setMaximumSize(QtCore.QSize(50, 25))
        self.remove_item_button.setAutoDefault(False)
        self.remove_item_button.setDefault(False)
        self.remove_item_button.setFlat(False)
        self.remove_item_button.setObjectName("remove_item_button")
        self.horizontalLayout.addWidget(self.remove_item_button)
        self.item_label = QtWidgets.QLabel(CartItem)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.item_label.sizePolicy().hasHeightForWidth())
        self.item_label.setSizePolicy(sizePolicy)
        self.item_label.setObjectName("item_label")
        self.horizontalLayout.addWidget(self.item_label)
        self.item_quantity_spinBox = QtWidgets.QSpinBox(CartItem)
        self.item_quantity_spinBox.setMinimumSize(QtCore.QSize(50, 0))
        self.item_quantity_spinBox.setSuffix("")
        self.item_quantity_spinBox.setPrefix("")
        self.item_quantity_spinBox.setMinimum(1)
        self.item_quantity_spinBox.setMaximum(99999)
        self.item_quantity_spinBox.setObjectName("item_quantity_spinBox")
        self.horizontalLayout.addWidget(self.item_quantity_spinBox)

        self.retranslateUi(CartItem)
        QtCore.QMetaObject.connectSlotsByName(CartItem)

    def retranslateUi(self, CartItem):
        _translate = QtCore.QCoreApplication.translate
        CartItem.setWindowTitle(_translate("CartItem", "Form"))
        self.remove_item_button.setText(_translate("CartItem", "Remove"))
        self.item_label.setText(_translate("CartItem", "item"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    CartItem = QtWidgets.QWidget()
    ui = Ui_CartItem()
    ui.setupUi(CartItem)
    CartItem.show()
    sys.exit(app.exec_())