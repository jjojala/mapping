import sys
import random
import csv
from PySide2 import QtCore, QtWidgets, QtGui

class Clazzifications:
    def __init__(self, file):
        super().__init__()

        self.clazzes = []   # [ clazz, group, groupId, clazzId, options, notes ]

        with open(file, 'r', encoding="utf8") as classifications:
            recordreader = csv.reader(classifications,
                                      delimiter=';',
                                      quoting=csv.QUOTE_NONE,
                                      skipinitialspace=True)
            for record in recordreader:
                clazz = {
                    'clazz' : record[0],
                    'group' : record[1],
                    'type' : record[2],
                    'groupId' : record[3],
                    'clazzId' : record[4],
                    'options' : record[5],
                    'notes' : record[6] }
                self.clazzes.append(clazz)
                #print(clazz)

    def getClazzes(self, clazzId):
        result = []
        for clazz in self.clazzes:
            if clazz['clazzId'] == clazzId:
                result.append(clazz)

        return result

class MainWidget(QtWidgets.QWidget):

    def __init__(self, clazzifications, clipboard):
        super().__init__()

        self.clazzifications = clazzifications
        self.clipboard = clipboard
        
        self.clazz = QtWidgets.QLineEdit("jepjep")
        self.desc = QtWidgets.QLabel("",alignment=QtCore.Qt.AlignCenter)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.clazz)
        self.layout.addWidget(self.desc)
        self.setLayout(self.layout)

        self.clazz.textChanged.connect(self.clazzIdChanged)
        self.clipboard.dataChanged.connect(self.clipboardDataChanged)

    @QtCore.Slot()
    def clipboardDataChanged(self):
        self.clazz.setText(self.clipboard.text())

    @QtCore.Slot()
    def clazzIdChanged(self):
        
        clazzes = self.clazzifications.getClazzes(self.clazz.text())
        if (len(clazzes) == 0):
            self.desc.setText("N/A")
        else:
            text = ""
            for clazz in clazzes:
                text = text + "<b>" + clazz['clazz'] + " (" + clazz['type'] + ")</b><br/>" + \
                       "<i>" + clazz['group'] + " (" + clazz['groupId'] + ")</i>" + "<hr/>"
    
            self.desc.setText(text)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    widget = MainWidget(Clazzifications("luokat.csv"), app.clipboard())
    widget.resize(200, 200)
    widget.show()

    sys.exit(app.exec_())
