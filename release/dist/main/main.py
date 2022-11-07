import sqlite3
import sys

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QWidget, QMessageBox


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.con = sqlite3.connect('coffee.sqlite')
        self.initUi()
        self.updTable()

    def initUi(self):
        self.AddBtn.clicked.connect(self.addString)
        self.ChangeBtn.clicked.connect(self.changeString)

    def addString(self):
        self.newString = String('new', '')
        self.newString.show()
        self.close()

    def changeString(self):
        self.newString = String('change', self.tableWidget.item(self.tableWidget.currentRow(),
                                             self.tableWidget.currentColumn()).text())
        self.newString.show()
        self.close()

    def updTable(self):
        cur = self.con.cursor()
        data = cur.execute('SELECT "название сорта", "степень обжарки", "молотый/в зернах",'
                           '"описание вкуса","цена","объем упаковки (в мл)" FROM Coffees').fetchall()
        self.tableWidget.setRowCount(len(data))
        self.tableWidget.setColumnCount(len(data[0]))
        self.tableWidget.setHorizontalHeaderLabels([i[0] for i in cur.description])
        for i, row in enumerate(data):
            for j, elem in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch)


class String(QWidget):
    def __init__(self, mode, name):
        super().__init__()
        self.mode = mode
        self.name = name
        self.con = sqlite3.connect('coffee.sqlite')
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.initUi()

    def initUi(self):
        if self.mode == 'new':
            self.SaveBtn.clicked.connect(self.save)
        elif self.mode == 'change':
            self.SaveBtn.clicked.connect(self.upd)
            self.InputName.setDisabled(True)
            self.SaveBtn.setText('Обновить')
            self.loadData()

    def save(self):
        cur = self.con.cursor()
        name, roasters, Type, price, volume = self.InputName.text(), self.RoastersBox.currentText(),\
            self.TypeBox.currentText(), self.InputPrice.text(), self.InputVolume.text()
        reply = QMessageBox.question(self, 'Сохранение', f'Данные\nНазвание - '
                f'{name}\nСтепень обжарки - {roasters}\n {Type}\nЦена - {price}\nОбъем (в мл) - '
                f'{volume}\nОписание вкуса - Снизу\nСохранить?', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            cur.execute(f'INSERT INTO Coffees("название сорта", "степень обжарки", '
                        f'"молотый/в зернах","описание вкуса", "цена", "объем упаковки (в мл)")'
                        f' VALUES("{name}", "{roasters}", "{Type}", "{self.textEdit.toPlainText()}",'
                        f' {price}, {volume})')
            self.con.commit()

    def upd(self):
        cur = self.con.cursor()
        name, roasters, Type, price, volume = self.InputName.text(), self.RoastersBox.currentText(),\
            self.TypeBox.currentText(), self.InputPrice.text(), self.InputVolume.text()
        reply = QMessageBox.question(self, 'Обновление', f'Данные\nСтепень обжарки - {roasters}'
            f'\n {Type}\nЦена - {price}\nОбъем (в мл) - {volume}\nОписание вкуса - Снизу'
            f'\nОбновить?', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            cur.execute(f'UPDATE Coffees SET "название сорта" = "{name}", "степень обжарки" = "'
                        f'{Type}", "молотый/в зернах" = "{Type}", "описание вкуса" = "'
                        f'{self.textEdit.toPlainText()}", "цена" = {price},'
                        f' "объем (в мл)" = {volume}')
        self.con.commit()

    def loadData(self):
        cur = self.con.cursor()
        data = cur.execute(f'SELECT * FROM Coffees WHERE "название сорта" = "{self.name}"').fetchone()
        name, price, volume = self.name, data[5], data[-1]
        self.InputName.setText(name)
        self.InputPrice.setText(str(price))
        self.InputVolume.setText(str(volume))
        self.textEdit.setText(f'{data[4]}')

    def closeEvent(self, event):
        ex.updTable()
        ex.show()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    app.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
    sys.excepthook = except_hook
    sys.exit(app.exec())
