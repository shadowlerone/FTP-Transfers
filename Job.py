import Photo
from pathlib import Path
import logging
from PIL import Image
from math import floor
import os


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


def apply_padding(i: float, pd):
	return floor(i*(1-2*pd))


class Job():
	AUTO = "AUTO"
	def __init__(self,
			FOLDER, 
			ASPECT_RATIO = DEFAULT_ASPECT_RATIO, 
			DATE=DEFAULT_DATE, 
			BACKGROUND = DEFAULT_BACKGROUND,
			PADDING_PERCENT=DEFAULT_PADDING_PERCENT,
			DARK = DEFAULT_DARK,
			SIZE = AUTO
	):
		self.ASPECT_RATIO = ASPECT_RATIO
		self.DATE = DATE
		self.BACKGROUND = BACKGROUND
		self.PADDING_PERCENT = PADDING_PERCENT
		self.DARK = DARK
		self.size = SIZE

		self.FOLDER = Path(FOLDER)

POST_JOB_2 = Job(Path("post_2"), ASPECT_RATIO= Job.AUTO)


class JobInstance():
	def __init__(self, job: Job, photo: Photo):
		self.JOB = job
		self.photo = photo
		self.set_aspect_ratio()
		self.set_sizes()
		self.set_thumbnail()
		self.set_final_sizes()

	def set_aspect_ratio(self):
		if (self.JOB.ASPECT_RATIO == Job.AUTO):
			self.aspect_ratio = self.photo.aspect_ratio
		else:
			self.ar = self.JOB.ASPECT_RATIO

	def set_sizes(self):
		if self.JOB.size == Job.AUTO:
			self.width, self.height = self.photo.width, self.photo.height
			self.size = (self.width, self.height)
		else:
			self.width, self.height = self.size
		self.target_width, self.target_height =apply_padding(self.width, self.JOB.PADDING_PERCENT) , apply_padding(self.height, self.JOB.PADDING_PERCENT)

	def set_thumbnail(self):
		self.photo.set_thumbnail((self.target_width, self.target_height))

	def set_final_sizes(self):
		final_width, final_height = self.photo.thumbnail.size
		# print(width, height)
		self.top = (self.height-final_height)//2
		self.left = (self.width-final_width)//2

	def __call__(self):
		try:
			with Image.open(self.photo.filepath) as img:
				result = Image.new(img.mode,self.size, self.JOB.BACKGROUND)
				os.makedirs(self.JOB.FOLDER,exist_ok=True)
				logging.debug("pasting image")
				result.paste(self.photo.thumbnail, (self.left, self.top))
				logging.debug("saving padded image")
				result.save(Path(self.JOB.FOLDER)/Path(self.photo.filepath).name, "JPEG", quality=60)
		except:
			logging.exception('')
