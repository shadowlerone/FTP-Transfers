import json
from queue import Queue
# from main import Photo
from pathlib import Path

class Queueable():
	Queued = {}


class QueueManager():
	q: Queue
	fp: str
	def __init__(self, queuable: Queueable, filepath:str, queue = None):
		self.fp = filepath
		self.queueable = queuable
		if queue:
			self.q = Queue()
		else:
			self.q = Queue()
		# self.load()
	
	def qsize(self):
		return self.q.qsize()
	
	def empty(self):
		return self.q.empty()

	def full(self):
		return self.q.full()
	
	def put(self, item, block=True,timeout=None, save = True):
		self.q.put(item, block, timeout)
		if save:
			self.save()
			# TODO save to file
	
	def get(self, block = True, timeout = None, save = True):
		o = self.q.get(block, timeout)
		if save:
			self.save()
		return o
	def task_done(self):
		return self.q.task_done()
	
	def join(self):
		return self.q.join()

	def save(self):
		with open(self.fp, "w") as file:
			json.dump([i.file_path for i in list(self.q.queue)], file)
	
	def load(self):
		if Path(self.fp).is_file():
			with open(self.fp) as file:
				temp_q = json.load(file)
				for i in temp_q:
					if i not in self.queuable.Queued.keys():
						self.put(type(self.queuable)(i), save = False)
		else:
			self.save()
