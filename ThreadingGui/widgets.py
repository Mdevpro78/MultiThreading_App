import os
import json

from urllib3 import PoolManager
from PySide2.QtGui import QFont
from PySide2.QtWidgets import (
	QWidget, QLabel,
	QProgressBar, QLineEdit,
	QPushButton, QTextEdit,
	QFileDialog, QGridLayout,
	QMessageBox
)
from PySide2.QtCore import QThreadPool, QTimer

from ThreadingGui.workers import UrlWorker


class GUI(QWidget):
	
	def __init__(self):
		super().__init__()
		self.initialize_ui()
		self.threadpool = QThreadPool()
		self.url_counter = 0
		self.num_pools = 20
	
	def initialize_ui(self):
		self.setMinimumSize(1000, 700)
		self.setWindowTitle('Threading App')
		self.setup()
		self.show()
		self.timer_widget = TimerWidget()
	
	def setup(self):
		dir_label = QLabel("Choose Json source files:")
		self.src_line_edit = QLineEdit()
		self.src_line_edit.setPlaceholderText("Select a Json File That Contains The Urls")
		
		src_button = QPushButton('Browse')
		src_button.setToolTip("Select Input Json File.")
		src_button.clicked.connect(self.set_json_file)
		
		dist_button = QPushButton('Browse')
		dist_button.setToolTip("Select Output Json File ")
		dist_button.clicked.connect(self.set_destination_json)
		
		self.dist_line_edit = QLineEdit()
		self.dist_line_edit.setPlaceholderText("Select Destination Json File")
		
		self.thread_pool_length = QLineEdit()
		self.thread_pool_length.setPlaceholderText("Enter length of thread pool")
		
		
		start_button = QPushButton("Start")
		start_button.setToolTip('Click to Run')
		start_button.clicked.connect(self.start)
		
		self.display_board = QTextEdit()
		self.display_board.setReadOnly(True)
		
		self.progress_bar = QProgressBar()
		self.progress_bar.setValue(0)
		
		grid = QGridLayout()
		grid.addWidget(dir_label, 0, 0)
		grid.addWidget(self.src_line_edit, 1, 0)
		grid.addWidget(src_button, 1, 2)
		grid.addWidget(self.dist_line_edit, 2, 0)
		grid.addWidget(dist_button, 2, 2)
		grid.addWidget(start_button, 4, 2)
		grid.addWidget(self.thread_pool_length, 4, 0)
		grid.addWidget(self.display_board, 5, 0, 1, 3)
		grid.addWidget(self.progress_bar, 6, 0, 4, 3)
		
		self.setLayout(grid)
	
	def set_json_file(self):
		file_dialog = QFileDialog(self)
		dialog_window = file_dialog.getOpenFileName(self,
		                                            "Select Json file",
		                                            '../jsons',
		                                            "Json files (*.json)")
		self.src_json = dialog_window[0]
		if self.src_json:
			try:
				with open(self.src_json, 'r') as json_file:
					self.urls = json.load(json_file)['urls']
			except KeyError:
				raise KeyError('Please enter a valid json file')
			
			self.src_line_edit.setText(self.src_json)
			
		self.number_of_urls = len(self.urls)
		self.progress_bar.setRange(0, self.number_of_urls)
	
	def set_destination_json(self):
		file_dialog = QFileDialog(self)
		file_dialog.setFileMode(QFileDialog.Directory)
		dialog_window = file_dialog.getOpenFileName(self,
		                                            "Select Json file",
		                                            '../jsons',
		                                            "Json files (*.json)")
		self.dist_path = dialog_window[0]
		if self.dist_path:
			self.dist_line_edit.setText(self.dist_path)
	
	def start(self):
		self.timer_widget.timer.start()
		num_pools = self.thread_pool_length.text()
		if num_pools.isdigit():
			self.num_pools = int(num_pools)
		# print(self.num_pools)
		manager = PoolManager(num_pools = self.num_pools)
		self.url_counter = 0
		self.timer_widget.timer_counter = 0
		self.progress_bar.setValue(0)
		self.display_board.clear()
		self.display_board.append("...................... Starting ......................")
		self.display_board.append("indexs\t|number of urls\t|responses")
		
		if self.src_json != "" and self.dist_path != "":
			self.threadpool.setStackSize(self.number_of_urls ** 2)
			self.threadpool.setMaxThreadCount(self.number_of_urls)
			for index, url in enumerate(self.urls):
				worker = UrlWorker(index, url, self.number_of_urls, manager)
				worker.signals.result.connect(self.update_text_edit)
				worker.signals.progress.connect(self.update_progressbar)
				worker.signals.finished.connect(self.save_data)
				worker.signals.open_dir.connect(self.finish_messagebox)
				
				self.threadpool.start(worker)
	
	def update_progressbar(self):
		self.url_counter += 1
		self.progress_bar.setValue(self.url_counter)
	
	def update_text_edit(self, data):
		index, url, url_length = data
		self.display_board.append(f"{index}\t|{url_length}\t\t| [GET] response from {url}")
	
	def save_data(self, header_data):
		data = json.dumps(header_data, indent = 2)
		with open(f'{self.dist_path}', 'w') as f:
			f.write(data)
	
	def finish_messagebox(self):
		dlg = QMessageBox(self)
		dlg.setWindowTitle("Finished")
		dlg.setText("Do you want to open result file?")
		self.timer_widget.timer.stop()
		dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
		dlg.setIcon(QMessageBox.Question)
		button = dlg.exec_()
		if button == QMessageBox.Yes:
			self.open_file()
	
	def open_file(self):
		cmd = 'start {}'.format(self.dist_path)
		os.system(cmd)


class TimerWidget(QWidget):
	
	def __init__(self):
		super(TimerWidget, self).__init__()
		
		self.setMinimumSize(400, 30)
		self.setup()
		self.show()
	
	def setup(self):
		font = QFont()
		font.setWeight(100)
		self.setWindowTitle('Threading Timer Window')
		self.timer_counter = 0
		self.timer_label = QLabel("Timer:\t")
		self.timer_label.setFont(font)
		self.timer = QTimer()
		self.timer.setInterval(1000)
		self.timer.timeout.connect(self.increase_timer)
		reset_btn = QPushButton('Reset')
		reset_btn.clicked.connect(self.reset)
		grid = QGridLayout()
		grid.addWidget(self.timer_label, 0, 0)
		grid.addWidget(reset_btn, 0, 1)
		self.setLayout(grid)
	
	def increase_timer(self):
		self.timer_counter += 1
		self.timer_label.setText(f"Timer: {self.timer_counter} s")
	
	def reset(self):
		self.timer_label.setText("Timer:\t")
