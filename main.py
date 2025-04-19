
# import time module, Observer, FileSystemEventHandler
# from genericpath import isfile
from genericpath import isfile
import json
import queue
import shutil
import subprocess
import threading
import time
from watchdog.observers import Observer
# from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler
import exiftool
import datetime
import os.path
from pathlib import Path
import os
from PIL import Image
import logging
from math import floor
from queue import Queue
from QueueManager import QueueManager
from Job import Job, JobInstance, POST_JOB_2
from Photo import Photo

WHITE = (255,255,255)
TRANSPARENT = (0,0,0, 0)
BLACK = (0,0,0)
ORANGE = (255, 92, 00)

DEFAULT_BACKGROUND = WHITE
FONT_SIZE = 14
DEFAULT_DATE = False
DEFAULT_DARK = False

DEFAULT_ASPECT_RATIO = (5/4)
# DEFAULT_ASPECT_RATIO = (1/1)
DEFAULT_PADDING_PERCENT = 1/12




BASEDIR = Path.home()

def min_max(i):
	return min(i), max(i)

def apply_padding(i: float, pd):
	return floor(i*(1-2*pd))


class OnMyWatch:
	def __init__(self, wd= os.path.join(BASEDIR, "Pictures", "server")):
		self.observer = Observer()
		self.watchDirectory =wd

	def run(self):
		event_handler = Handler()
		self.observer.schedule(event_handler, self.watchDirectory, recursive = True)
		self.observer.start()
		
class Handler(FileSystemEventHandler):

	@staticmethod
	def on_any_event(event):
		if event.is_directory:
			return None
		if "tmp" not in event.src_path and ".jpg" in event.src_path.lower():
			if event.event_type == "created" or event.event_type == "modified" or event.event_type == "moved":
				if event.src_path not in Photo.Queued.keys():
					logging.info(f"Adding {event.src_path} to the queue")
					photos.put(Photo(event.src_path))
				else:
					logging.debug(f"updating {event.src_path} in the queue")
					logging.debug(f"Updated {(datetime.datetime.now() - Photo.Queued[event.src_path].created).total_seconds()} seconds after previous update")

					Photo.Queued[event.src_path].update()
			else:
				logging.debug(event.event_type)
			

def new_name(original, i =0):
	p = Path(original)
	# p.stem
	if i == 0:
		if p.is_file():
			return new_name(original, i+1)
		else:
			return original
	else:
		temp = p.with_stem(p.stem + f" ({i})")
		if not temp.is_file():
			return temp
		else:
			return new_name(original, i+1)


def worker():
	logging.info("starting sorting thread")
	while True:
		item = photos.get()
		if (datetime.datetime.now() - item.created).total_seconds() <  Photo.BASE_WAIT_TIME * (2**(item.attempts-1)):
			photos.put(item)
			continue

		logging.debug(f'Working on {item}')
		# try:
		item.process()
		pad_queue.put(item)

		# except:
		# 	if (item.attempts > Photo.MAX_ATTEMPTS):
		# 		logging.exception(f"unknown error processing file. {item.attempts}/{Photo.MAX_ATTEMPTS}, marking as done for now. TODO: IMPLEMENT ERROR CHECKING")
		# 	else: 
		# 		logging.warning(f"unknown error processing file {item.file_path}. attempt {item.attempts}/{Photo.MAX_ATTEMPTS}\nWaiting {Photo.BASE_WAIT_TIME * (2**item.attempts)} seconds before next attempt.")
		# 		photos.put(item)
		# 		continue

			# logging.warning()
		# print(item.file_name)
		logging.debug(f'Finished {item}')
		photos.task_done()
	

def pad():
	logging.info("starting padding thread")
	while True:
		item = pad_queue.get()
		try:
			logging.info(f'Padding {item}')
			item.pad()
			JI = JobInstance(POST_JOB_2, item)
			JI()
		except:
			logging.exception(f"unknown error processing file. {item.attempts}/{Photo.MAX_ATTEMPTS}, marking as done for now. TODO: IMPLEMENT ERROR CHECKING")
			pad_queue.put(item)
			# pass
		else:
			logging.info(f'Finished padding {item}')
			pad_queue.task_done()

# def ftpcopy():
# 	logging.info("Starting ftpcopy thread")
# 	while True:
# 		subprocess.call("ftpcopy -u canonr6mk2@shadowlerone.ca -p T1MJ%{76yRcV ftp://ftp.shadowlerone.ca/ ../server", shell=True)
# 		# logging.info("Done copying. Sleeping now.")
# 		time.sleep(10)
	

if __name__ == '__main__':
	print("Starting")
	logging.basicConfig(level=logging.INFO)
	# threading.Thread(target=ftpcopy, daemon=True).start()
	logging.info("Initializing Queues")
	photos = QueueManager(Photo, "photo_q")
	pad_queue = QueueManager(Photo, "pad_q")
	threading.Thread(target=worker, daemon=True).start()
	threading.Thread(target=worker, daemon=True).start()
	threading.Thread(target=worker, daemon=True).start()
	threading.Thread(target=worker, daemon=True).start()
	threading.Thread(target=pad, daemon=True).start()
	threading.Thread(target=pad, daemon=True).start()
	
	# watch2 = OnMyWatch()
	# watch2.run()

	watch = OnMyWatch(os.path.join(BASEDIR, "FTP-Transfers", "drop"))
	watch.run()
	# pad_queue.load()
	# photos.load()
	watch.observer.join()

	""" try:
		while True:
			time.sleep(1)
	except:
		pass
		# self.observer.stop()
		# print("Observer Stopped") """
