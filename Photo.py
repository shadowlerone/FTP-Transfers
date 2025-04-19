import exiftool
import logging
import datetime
from pathlib import Path
import os
from PIL import Image
import time
import shutil
from math import floor
import QueueManager
# from Job import JobInstance, POST_JOB_2

# BASEDIR = Path.home()
# PADDING_PERCENT = 1/24
# WHITE = (255,255,255)

def min_max(i):
	return min(i), max(i)

class Photo(QueueManager.Queueable):
	MAX_ATTEMPTS = 10
	BASE_WAIT_TIME = 5
	def __init__(self, f):
		self.processed = False
		self.file_path = f 
		self.created = datetime.datetime.now()
		Photo.Queued[f] = self
		self.destination_fp = ""
		self.attempts = 0
		self.date_taken = None
		self.folder = None
		self.tags = None
		

		self.height = None
		self.width = None
		self.aspect_ratio = None
		self.smaller_side = None
		self.bigger_side = None

		self.filepath = None
		self.data = None
		self.thumbnail = None

	def gen_tags(self):
		# with exiftool.ExifToolHelper() as et:
		# 	self.tags = et.get_metadata(self.file_path)[0]
		# 	if len(et.get_metadata(self.file_path)) > 1:
		# 		logging.warning("Tags greater than 1.")
		# self.date_taken = datetime.datetime.strptime(
		# 	self.tags["EXIF:DateTimeOriginal"], 
		# 							  "%Y:%m:%d %H:%M:%S")
		# 2024:04:21 13:35:11
		with Image.open(self.file_path) as img:
			self.date_taken = datetime.datetime.strptime(img._getexif()[36867], "%Y:%m:%d %H:%M:%S")
		self.folder = Path(
			os.path.join(
				self.date_taken.strftime("%Y"), 
				self.date_taken.strftime("%Y-%m"), 
				self.date_taken.strftime("%Y-%m-%d")
			)
		)

	def compute_filepath(self):
		filepath = self.file_path
		if (Path(self.file_path).is_file()):
			filepath = self.file_path
		elif (Path(self.destination_fp).is_file()):
			filepath = self.destination_fp
		else:
			logging.warning(f"No file found at {self.file_path} or {self.destination_fp}")
			# return
			raise Exception(f"No file found at {self.file_path} or {self.destination_fp}")
			
		# return filepath
		self.filepath = filepath
	
	def set_sizes(self, filepath):
		with Image.open(filepath) as img:
			self.height, self.width = img.size[1], img.size[0]
			self.aspect_ratio = img.size[1] / img.size[0]
			self.smaller_side, self.bigger_side = min_max(img.size)
			
	def set_thumbnail(self, size):
		if (self.thumbnail == None or not (self.thumbnail.size[0] == size[0] or self.thumbnail.size[1] == size[1])):
			with Image.open(self.filepath) as img:
				self.thumbnail = img.copy()
				self.thumbnail.thumbnail(size)


	def print(self):
		for k, v in self.tags.items():
			print(f"Dict: {k} = {v}")

	def pad(self):
		if not (self.folder and self.date_taken):
			self.gen_tags()
		# outpath = ( Path(os.path.join("processed")))
		# os.makedirs(outpath / "Instagram", exist_ok=True)
		# os.makedirs(outpath / "Full Size", exist_ok=True)
		# outpath.mkdir(parents=True, exist_ok=True)
		try:
			self.compute_filepath()
		except:
			logging.exception('')
			return
		self.set_sizes(self.filepath)


		# shutil.copy2(filepath, copy_outfile)
		# self.pad_image(filepath, outfile)
		# self.pad_image(filepath, outfile_full, instagram=False)


			# img.save(copy_outfile, "JPEG", quality=100, exif=data)
	def pad_image(self, filepath, outfile, instagram=True):
		
		pass
		# with Image.open(filepath) as img:
		# 	# bigger_side = max(img.size)
		# 	# bigger_side = 1080
		# 	left = 0
		# 	top = 0
		# 	try:
		# 		data = img.info['exif']
		# 	except KeyError:
		# 		data = None
		# 	width, height = 1080, 1080
		# 	if not instagram:
		# 		width, height = 2000, 2000
		# 	target_width, target_height = floor(width*(1-2*PADDING_PERCENT)), floor(height*(1-2*PADDING_PERCENT))
		# 	img.thumbnail((target_width, target_height))
		# 	# top = (bigger_side-target_height)//2
		# 	# left = (bigger_side-target_width)//2
		# 	top = (height-img.size[1])//2
		# 	left = (width-img.size[0])//2
		# 	result = Image.new(img.mode, (width, height), WHITE)
		# 	result.paste(img, (left, top))
		# 	result.save(outfile, "JPEG", quality=60, exif=data)


	def process(self):
		self.attempts += 1
		self.gen_tags()
		# (Path("Pictures/Catalog") / self.folder).mkdir(parents=True, exist_ok=True) # TODO: rewrite folder handling, move to main
		# self.destination_fp =  Path("Pictures/Catalog") / self.folder / Path(self.file_path).name
		# if (self.destination_fp.is_file()):
		# 	logging.warning(f"TODO: FILE HANDLING WHEN FILE ALREADY EXISTS: {self.destination_fp}")
		# else:
		# 	# self.pad()
		# 	shutil.move(self.file_path, self.destination_fp)

			# return
		# self.destination_fp = new_name(self.destination_fp)
		
		# if ("XMP:Rating" in self.tags.keys() and self.tags["XMP:Rating"] >= 1 and Path(self.file_path).suffix.lower() == ".jpg"):
		pass

	def update(self):
		self.attempts = 0
		self.created = datetime.datetime.now()

	def __str__(self):
		return self.file_path

