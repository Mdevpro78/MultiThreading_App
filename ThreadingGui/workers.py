import re
import time

# from urllib3 import PoolManager

from PySide2.QtCore import (
	QObject,
	QRunnable,
	Slot,
	Signal
)


DATA = {}
COUNT = 1

# HTTP = PoolManager(num_pools = 20)


class UrlSignals(QObject):
	result = Signal(tuple)
	progress = Signal()
	finished = Signal(dict)
	open_dir = Signal()


class UrlWorker(QRunnable):
	def __init__(self, index, url, num_urls, manager):
		super(UrlWorker, self).__init__()
		self.index = index
		self.url = url
		self.num_urls = num_urls
		self.manager = manager
		self.signals = UrlSignals()

	@Slot()
	def run(self):
		response = self.manager.request('GET', self.url)
		data = response.data.decode('utf-8')
		regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
		matches = re.findall(regex, data)
		number_of_urls = len(list(matches))
		
		DATA.update({
			f'{self.url}': {
				'links': list(matches)
			}
		})
		self.signals.result.emit((self.index, self.url, number_of_urls))
		self.signals.progress.emit()
		self.signals.finished.emit(DATA)
		global COUNT
		if self.num_urls == COUNT:
			time.sleep(0.5)
			self.signals.open_dir.emit()
			COUNT = 1
		COUNT += 1
