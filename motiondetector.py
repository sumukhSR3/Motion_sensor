import os
import numpy as np
import cv2 as cv
from time import time
from datetime import datetime

class MotionDetector():
	def __init__(self, cam_idx=0, esc=27, thresh=8, patience=30, annotate=False):
		self.esc = esc
		self.thresh = thresh
		self.patience = patience
		self.annotate = annotate
		self.move_time = None #time of move if move in last patience seconds, else none
		self.cap = cv.VideoCapture(cam_idx)
		self.img = self.cap.read()[1]
		self.height, self.width, _ = self.img.shape
		self.gray = self.to_gray(self.img)
		self.codec = cv.VideoWriter_fourcc('M','J','P','G')
		if not os.path.exists('videos'): os.mkdir('videos')

	def to_gray(self, img):
		gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
		gray = cv.GaussianBlur(gray, (21,21), 0)
		return gray

	def get_delta(self):
		gray2 = self.to_gray(self.img)
		delta = cv.absdiff(self.gray, gray2)
		# cv.imshow('1', delta)
		delta = cv.threshold(delta, self.thresh, 255, cv.THRESH_BINARY)[1]
		# cv.imshow('2', delta)
		self.delta = cv.dilate(delta, None, iterations=3)
		self.hasMovement = bool(self.delta.sum())
		self.gray = gray2

	def initialize_recorder(self):
		folder = 'videos/'+datetime.now().strftime('%I:%M:%S-%A%d%B%Y')+'/'
		os.mkdir(folder)
		del_name = folder+'delta.avi'
		img_name = folder+'feed.avi'
		self.delwriter = cv.VideoWriter(del_name, self.codec, 30, (self.width, self.height), isColor=False)
		self.imgwriter = cv.VideoWriter(img_name, self.codec, 30, (self.width, self.height))
		self.move_time = time()

	def write_recorder(self):
		self.delwriter.write(self.delta)
		self.imgwriter.write(self.img)

	def update_recorder(self):
		if self.hasMovement and self.move_time: # is recording
			self.move_time = time()
			self.write_recorder()
		elif self.hasMovement and not self.move_time:
			cur_time = datetime.now().strftime('%I:%M:%S')
			print(cur_time+' - Began recording.')
			self.initialize_recorder()
			self.write_recorder()
		elif not self.hasMovement and self.move_time:
			if time() <= self.move_time + self.patience:
				self.write_recorder()
			else:
				cur_time = datetime.now().strftime('%I:%M:%S')
				print(cur_time+' - Finished recording.\n')
				self.move_time = None

	def display_feeds(self):
		cv.imshow('Main Feed', self.img)
		cv.imshow('Movement', self.delta)

	def add_info(self):
		cur_time = datetime.now().strftime('%I:%M:%S')
		cv.putText(self.img, cur_time, (10, self.height-10), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 1)
		text = 'Movement Detected' if self.hasMovement else 'No Movement'
		cv.putText(self.img, text, (10,20), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 1)
		if not self.annotate or not self.hasMovement: return
		(x,y,w,h) = cv.boundingRect(self.delta)
		cv.rectangle(self.img, (x,y), (x+w,y+h), (0,255,0), 2)

	def check_exit(self):
		k = cv.waitKey(10)
		if k == self.esc:
			self.cap.release()
			exit()

	def run(self):
		while self.cap.isOpened():
			self.img = self.cap.read()[1]
			self.get_delta()
			self.add_info()
			self.update_recorder()
			self.display_feeds()
			self.check_exit()

if __name__ == '__main__':
	agent = MotionDetector()
	agent.run()