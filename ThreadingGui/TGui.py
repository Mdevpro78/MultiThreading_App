import sys
from PySide2.QtWidgets import QApplication

from ThreadingGui.widgets import GUI


style_sheet = """
    QProgressBar{
        background-color: #C0C6CA;
        color: black;
        border: 5px solid grey;
        padding: 3px;
        font_size: 15px;
        height: 30px;
        text-align: center;
    }
    QProgressBar::chunk{
        background: #32CD30;
        width: 10px;
    }
    QPushButton {
        border: 2px solid #8f8f91;
        border-radius: 5px;
        min-width: 150px;
        height: 30px;
        font-size: 20px;
        background-color: #ed7327;
	}
	QLineEdit {
        border: 2px solid #B4FEE7;
        border-radius: 6px;
        padding: 0 8px;
        height: 30px;
        font-size: 20px;
        background: white;
        color: black;
        selection-background-color: darkgray;
	}
	QTextEdit{
        background-color: white;
        color: black;
        font-size: 20px;
	}
	QLabel {
        font-size: 20px;
	}
"""

if __name__ == "__main__":
	app = QApplication(sys.argv)
	app.setStyleSheet(style_sheet)
	window = GUI()
	sys.exit(app.exec_())
