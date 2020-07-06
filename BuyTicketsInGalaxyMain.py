#!/usr/bin/env python
# -*- coding: utf-8 -*-
import OrdersFromCLOTAUI
import sys
from PyQt5 import QtWidgets
import OrdersFromCLOTAFun

class MyWidget(QtWidgets.QWidget,OrdersFromCLOTAUI.Ui_Form):
    def __init__(self,parent=None):
        super(MyWidget,self).__init__(parent)
        self.setupUi(self)



if __name__ == "__main__":
    OrdersFromCLOTAFun.InitLogger()
    app =  QtWidgets.QApplication(sys.argv)
    mf=MyWidget()
    mf.show()
    sys.exit(app.exec_())
