import logging
from math import floor
from pathlib import Path
import queue
import threading
from PIL import Image, ImageDraw, ImageFont
import logging
import os
import sys
from datetime import datetime
from multiprocessing import Pool
from multiprocessing.connection import Listener
import copy


def get_data(img: Image.Image):
	try:
		data = img.info['exif']
	except KeyError:
		# logging.debug()
		logging.exception("Exif data not found.")
		data = None

	return data

class Job():
	AUTO = "AUTO"
	def __init__(self,
			  FOLDER, 
			  ASPECT_RATIO = DEFAULT_ASPECT_RATIO, 
			  DATE=DEFAULT_DATE, 
			  BACKGROUND = DEFAULT_BACKGROUND,
			  PADDING_PERCENT=DEFAULT_PADDING_PERCENT,
			  DARK = DEFAULT_DARK
	):
		self.ASPECT_RATIO = ASPECT_RATIO
		self.DATE = DATE
		self.BACKGROUND = BACKGROUND
		self.PADDING_PERCENT = PADDING_PERCENT
		self.DARK = DARK

		self.FOLDER = Path(FOLDER)

	def append_folder(self, f):
		self.FOLDER = Path("-".join([str(self.FOLDER), f]))
	
	def get_aspect_ratio(self, img: Image.Image):
		if (self.ASPECT_RATIO == Job.AUTO):
			ar = img.size[1] / img.size[0]
		else:
			ar = self.ASPECT_RATIO
		return ar
	def get_size(img: Image.Image, ar): 
		return img.size[0], floor(img.size[0] * ar)
	def get_target_size(self, width, height):
		return floor(width*(1-2*self.PADDING_PERCENT)), floor(height*(1-2*self.PADDING_PERCENT))
	
	def min_max(i):
		return min(i), max(i)

	def compute_sizes(self, img: Image.Image):
		self.smaller_side, self.bigger_side = self.min_max(img.size)
		self.left = self.top = 0
		self.data = get_data(img)
		ar = self.get_aspect_ratio(img)
		self.width, self.height = self.get_size(img, ar)
		self.target_width, self.target_height = self.get_target_size(self.width, self.height)
		
		logging.debug("Generating white background")
		self.result = Image.new(img.mode, (self.width, self.height), self.BACKGROUND)
		logging.debug("Pasting image over white background")

		self.resized_image = img.copy()
		self.resized_image.thumbnail((self.target_width,self.target_height))
		
		final_width, final_height = resized_image.size
		# print(width, height)
		self.top = (self.height-final_height)//2
		self.left = (self.width-final_width)//2

	# def date(self, img):
	# 	try:
	# 		logging.debug("Finding date")
	# 		image_date = datetime.strptime(img._getexif()[36867], "%Y:%m:%d %H:%M:%S")
	# 		logging.debug("loading image to write date")
	# 		text_image = Image.new("RGBA", (self.width, self.height),TRANSPARENT)
	# 		draw = ImageDraw.Draw(text_image)
	# 		logging.debug("getting dpi")
	# 		dpi = img.info['dpi'][0]
	# 		logging.debug(f"dpi: {dpi}")
	# 		font_size = (dpi/72) * self.FONT_SIZE
	# 		if self.ASPECT_RATIO == self.STORY_JOB.ASPECT_RATIO:
	# 			font_size *= 1.5
	# 		logging.debug(f"font size: {font_size}")
	# 		FONT = ImageFont.truetype(self.font, size=font_size)
			
	# 		image_date_string = image_date.strftime("%Y-%m-%d")
	# 		logging.debug(f"date string: {image_date_string}")
	# 		text_w = draw.textlength(image_date_string, FONT)
	# 		text_h = font_size

	# 		# Square: bottom corner
	# 		# horizontal: below image, right align, horizontal
	# 		# vertical: right of image, left align, rotated 90deg (vertical)

	# 		# x = (target_width - text_w)*(1-j.PADDING_PERCENT/4) + left
	# 		# y = (target_height - text_h)*(1-j.PADDING_PERCENT/4) + top 
			
	# 		x = self.final_width + self.left - text_w
	# 		y = self.final_height + self.top

	# 		# if img.size[0]/img.size[1] > 1.2:
	# 		# 	y += text_h*(1+j.PADDING_PERCENT*2)
	# 		# if img.size[1]/img.size[0] > 1.2:
	# 		# 	y = left - text_h*(1+j.PADDING_PERCENT*2)
	# 		# 	x = top + text_w*(j.PADDING_PERCENT)
	# 		x = floor(x)
	# 		y = floor(y)
	# 		logging.debug(f"x, y: {x}, {y}")
	# 		# logging.debug(f"x_offset, y_offset: {x_offset}, {y_offset}")
	# 		logging.debug("writing text")
	# 		if not self.DARK:
	# 			fill_color = WHITE
	# 			border_color = BLACK
	# 		else:
	# 			fill_color = ORANGE
	# 			border_color = TRANSPARENT
	# 		# for i in range(1, 1):
	# 		draw.text((x-1, y-1), image_date_string, font=FONT, fill=border_color)
	# 		draw.text((x+1, y-1), image_date_string, font=FONT, fill=border_color)
	# 		draw.text((x-1, y+1), image_date_string, font=FONT, fill=border_color)
	# 		draw.text((x+1, y+1), image_date_string, font=FONT, fill=border_color)
	# 		draw.text((x, y), image_date_string, font=FONT, fill=fill_color)
	# 		# if img.size[1]/img.size[0] > 1.2:
	# 		# 	text_image = text_image.rotate(90)
	# 		logging.debug("text written")
	# 	except KeyError:
	# 		logging.exception('')
			
	# 	logging.info("saving dated image")
	# 	result.paste(text_image, (0,0), text_image)
	# 	result.save(outpath, "JPEG", quality=100, exif=data)

	def __call__(self, photo):
		try:
			with Image.open(f) as img:
				self.compute_sizes()
				# print(top, left)
				logging.debug("pasting image")
				self.result.paste(self.resized_image, (self.left, self.top))
				logging.debug("saving padded image")
				self.result.save(outpath, "JPEG", quality=100, exif=data)
				
				# if not self.DATE:
				# 	self.result.save(outpath, "JPEG", quality=100, exif=data)

				# if self.DATE:
				# 	self.date()
		except:
			logging.exception('')


def pad(photo, j:Job):
		if not (photo.tags and photo.folder and photo.date_taken):
			photo.gen_tags()
		# os.makedirs(outpath / "Instagram", exist_ok=True)
		# os.makedirs(outpath / "Full Size", exist_ok=True)
		# outfile = outpath / "Instagram" /f"{photo.date_taken.strftime('%Y-%m-%d')}-{Path(photo.file_path).stem}-{Path(photo.file_path).suffix}"
		# outfile_full = outpath / "Full Size" / f"{photo.date_taken.strftime('%Y-%m-%d')}-{Path(photo.file_path).stem}-{Path(photo.file_path).suffix}"
		# # copy_outfile = outpath / f"{self.date_taken.strftime('%Y-%m-%d')}-{Path(self.file_path).name}"
		# # logging.info(outpath)
		# outpath.mkdir(parents=True, exist_ok=True)
		

		filepath = photo.file_path
		if (Path(photo.file_path).is_file()):
			filepath = photo.file_path
		elif (Path(photo.destination_fp).is_file()):
			filepath = photo.destination_fp
		else:
			logging.warning(f"No file found at {photo.file_path} or {photo.destination_fp}")
			return
		# shutil.copy2(filepath, copy_outfile)
		photo.pad_image(filepath, outfile)
		photo.pad_image(filepath, outfile_full, instagram=False)