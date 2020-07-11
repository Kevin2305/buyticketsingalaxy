# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\placeorder.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import BuyTicketsInGalaxyFun

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(567, 585)
        self.calendarWidget = QtWidgets.QCalendarWidget(Form)
        self.calendarWidget.setGeometry(QtCore.QRect(40, 230, 351, 161))
        self.calendarWidget.setObjectName("calendarWidget")
        self.button_getproducts = QtWidgets.QPushButton(Form)
        self.button_getproducts.setGeometry(QtCore.QRect(430, 160, 75, 23))
        self.button_getproducts.setObjectName("button_getproducts")
        self.button_buyit = QtWidgets.QPushButton(Form)
        self.button_buyit.setGeometry(QtCore.QRect(430, 330, 75, 23))
        self.button_buyit.setObjectName("button_buyit")
        self.spinbox_ticketnumber = QtWidgets.QSpinBox(Form)
        self.spinbox_ticketnumber.setGeometry(QtCore.QRect(440, 260, 42, 22))
        self.spinbox_ticketnumber.setReadOnly(False)
        self.spinbox_ticketnumber.setAccelerated(False)
        self.spinbox_ticketnumber.setMinimum(1)
        self.spinbox_ticketnumber.setMaximum(5)
        self.spinbox_ticketnumber.setProperty("value", 1)
        self.spinbox_ticketnumber.setObjectName("spinbox_ticketnumber")
        self.listWidget = QtWidgets.QListWidget(Form)
        self.listWidget.setGeometry(QtCore.QRect(30, 10, 361, 191))
        self.listWidget.setObjectName("listWidget")
        self.textBrowser_showordereno = QtWidgets.QTextBrowser(Form)
        self.textBrowser_showordereno.setGeometry(QtCore.QRect(30, 430, 371, 131))
        self.textBrowser_showordereno.setObjectName("textBrowser_showordereno")
        self.linedit_custid = QtWidgets.QLineEdit(Form)
        self.linedit_custid.setGeometry(QtCore.QRect(430, 110, 71, 20))
        self.linedit_custid.setObjectName("linedit_custid")
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(420, 80, 101, 16))
        self.label.setObjectName("label")
        self.button_cleanit = QtWidgets.QPushButton(Form)
        self.button_cleanit.setGeometry(QtCore.QRect(430, 470, 75, 23))
        self.button_cleanit.setObjectName("button_cleanit")
        self.env_comboBox = QtWidgets.QComboBox(Form)
        self.env_comboBox.setGeometry(QtCore.QRect(430, 20, 81, 22))
        self.env_comboBox.setObjectName("env_comboBox")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)


        self.button_getproducts.clicked.connect(self.getproducts)
        self.button_buyit.clicked.connect(self.buyit)
        self.button_cleanit.clicked.connect(self.cleanit)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.button_getproducts.setText(_translate("Form", "Get Products"))
        self.button_buyit.setText(_translate("Form", "Buy it Now"))
        self.label.setText(_translate("Form", "Galaxy Customer ID"))
        self.button_cleanit.setText(_translate("Form", "Clean it"))

        self.setButtons(1,0,0)
        self.initENV()

    def initENV(self):
        self.env_comboBox.addItem('Stage/QA')
        self.env_comboBox.addItem('DEV/QA2')
        self.env_comboBox.addItem('SL/LT')

    def cleanit(self):
        self.textBrowser_showordereno.clear()

    def getproducts(self):
        self.listWidget.clear()

        if self.env_comboBox.currentText() == 'Stage/QA':
            BuyTicketsInGalaxyFun.env = 'qa'
        if self.env_comboBox.currentText() == 'DEV/QA2':
            BuyTicketsInGalaxyFun.env = 'dev'
        if self.env_comboBox.currentText() == 'SL/LT':
            BuyTicketsInGalaxyFun.env = 'lt'
        
        self.setButtons(0,0,0)
        custid = self.linedit_custid.text()

        self.worker = GetProductWorkder(custid)

        self.worker.huaisig.connect(self.showErrProducts)
        self.worker.haosig.connect(self.showGetProducts)
        self.worker.start()

        """
        flag,self.items = BuyTicketsInGalaxyFun.getProducts(custid)
        if flag > 0:
            for p in self.items:
                self.listWidget.addItem(p.toStringBrief())
            self.enableBuyit()
            return 0
        """
        #self.listWidget.addItem("No Items Or Customer ID Not Exists")
    
    def showGetProducts(self,items):
        self.items = items
        for i in items:
            self.listWidget.addItem(i.toStringBrief())
        self.setButtons(1,1,1)
        
    def showErrProducts(self,msg):
        self.listWidget.addItem(msg)
        self.setButtons(1,0,1)

    def setButtons(self,get,buy,clean):
        if get:
            self.button_getproducts.setEnabled(True)
        else:
            self.button_getproducts.setDisabled(True)
        if buy:
            self.button_buyit.setEnabled(True)
        else:
            self.button_buyit.setDisabled(True)
        if clean:
            self.button_cleanit.setEnabled(True)
        else:
            self.button_cleanit.setDisabled(True)


    """
    def checkItem(self):
        plu = self.listWidget.selectedItems()[0].text().split(",")[0]
        vd = self.calendarWidget.selectedDate().toString('yyyy-MM-dd')
        flag,item = BuyTicketsInGalaxyFun.checkItemAvailable(plu,self.items,vd)
        if flag > 0:
            #self.textBrowser_showordereno.append('{} is available for product {}'.format(vd,plu))
            return plu,item
        else:
            self.textBrowser_showordereno.append('{} is NOT available for product {}'.format(item,plu))
            return 0,0
    
    def buyit1(self):
        rpl = QtWidgets.QMessageBox.question(
            self,
            "Question?","Are You Sure? {}".format(self.listWidget.selectedItems()[0].text().split(",")[2]),
            QtWidgets.QMessageBox.Yes,QtWidgets.QMessageBox.No
            )
        if rpl == QtWidgets.QMessageBox.Yes:
            plu,item = self.checkItem()
            if plu:
                messageid = BuyTicketsInGalaxyFun.getNextMessageID()
                tktnum = int(self.spinbox_ticketnumber.text())
                customerid = self.linedit_custid.text()
                visitdate = self.calendarWidget.selectedDate().toString('yyyy-MM-dd')
                flag,ret_holdevent = BuyTicketsInGalaxyFun.holdEvents(plu,tktnum,item,visitdate,messageid)
                if flag:
                    flag,msg = BuyTicketsInGalaxyFun.confirmOrder(ret_holdevent,customerid,messageid)
                    if flag:
                        self.textBrowser_showordereno.append(msg)
                        return 0
                self.textBrowser_showordereno.append(ret_holdevent)
                return 1
    """
    def buyit(self):
        self.setButtons(0,0,0)
        plu = self.listWidget.selectedItems()[0].text().split(",")[0]
        visitdate = self.calendarWidget.selectedDate().toString('yyyy-MM-dd')
        messageid = BuyTicketsInGalaxyFun.getNextMessageID()
        tktnum = int(self.spinbox_ticketnumber.text())
        customerid = self.linedit_custid.text()
        items = self.items
        self.thread = BuyitWorker(plu,tktnum,visitdate,items,customerid,messageid)
        self.thread.sig.connect(self.showMSG)
        self.thread.start()

    def showMSG(self,msg):
        import re
        if not re.findall('Processing',msg):
            self.setButtons(1,1,1)
        self.textBrowser_showordereno.append(msg)

class GetProductWorkder(QtCore.QThread):
    huaisig = QtCore.pyqtSignal(str)
    haosig = QtCore.pyqtSignal(list)

    def __init__(self,customerid):
        super(GetProductWorkder,self).__init__()
        self.customerid = customerid

    def run(self):
        flag,items = BuyTicketsInGalaxyFun.getProducts(self.customerid)
        if flag > 0:
            self.haosig.emit(items)
        else:
            self.huaisig.emit("No Items Or Customer ID Not Exists")

class BuyitWorker(QtCore.QThread):
    sig = QtCore.pyqtSignal(str)
    def __init__(self,plu,tktnum,visitdate,items,customerid,messageid):
        super(BuyitWorker,self).__init__()
        self.plu = plu
        self.tktnum = tktnum
        self.visitdate = visitdate
        self.messageid = messageid
        self.customerid = customerid
        self.items = items

    def run(self):
        plu,item = self.checkItem()
        if plu:
            flag,ret_holdevent = BuyTicketsInGalaxyFun.holdEvents(plu,self.tktnum,item,self.visitdate,self.messageid)
            if flag:
                flag,msg = BuyTicketsInGalaxyFun.confirmOrder(ret_holdevent,self.customerid,self.messageid)
                if flag:
                    self.sig.emit(msg)
            else:
                self.sig.emit(ret_holdevent)


    def checkItem(self):
        plu = self.plu
        vd = self.visitdate
        flag,item = BuyTicketsInGalaxyFun.checkItemAvailable(plu,self.items,vd)
        if flag > 0:
            self.sig.emit('{} is available for product {}, Processing'.format(vd,plu))
            return plu,item
        else:
            self.textBrowser_showordereno.append('{} is NOT available for product {}'.format(item,plu))
            return 0,0