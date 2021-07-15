import pdftoc
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QComboBox, QFileDialog, QMessageBox)


class MyApp(QWidget):
    pdfInput = ""
    outputDirectory = ""
    wingExist = False

    def __init__(self):
        super().__init__()
        self.setUI()

    def setUI(self):
        grid = QGridLayout()
        self.setLayout(grid)
        ipselectButton = QPushButton('파일 선택', self)
        ipselectButton.clicked.connect(self.showDialog)
        self.pdfNameLabel = QLineEdit(self.pdfInput)

        grid.addWidget(QLabel('PDF 파일:'), 0, 0)
        grid.addWidget(self.pdfNameLabel, 0, 1)
        grid.addWidget(ipselectButton, 0, 2)

        self.fileLoadButton = QPushButton('목차 생성하기', self)
        self.fileLoadButton.clicked.connect(self.loadFile)
        grid.addWidget(self.fileLoadButton, 3, 0, 1, -1)
        self.fileLoadButton.setEnabled(False)

        self.setWindowTitle('PDF 목차 생성기')
        self.setGeometry(300, 300, 300, 150)
        self.show()

    def loadFile(self):
        try:
            self.pdfImage = pdftoc.pdftoc(self.pdfInput)
        except:
            QMessageBox.about(self, "에러 발생", "뭔가 잘못되었습니다.")
        else:
            QMessageBox.about(self, "작업 완료", "목차 생성이 완료되었습니다!")

    def showDialog(self):
        fname = QFileDialog.getOpenFileName(self, 'PDF 파일을 선택해주세요', './', 'PDF(*.pdf)')
        self.pdfInput = fname[0]
        self.pdfNameLabel.setText(self.pdfInput)
        if self.pdfInput:
            self.fileLoadButton.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
