import os
import numpy as np
import cv2 as cv
from time import time
from datetime import datetime

class MotionDetector():
	def __init__(self, cam_idx=0, esc=27, fps=30, thresh=8, patience=30, annotate=False):
		self.esc = esc # system's escape key number
		self.thresh = thresh # changes in pixel intensity >= thresh are considered movement
		self.fps = fps # frame rate at which to save video
		self.patience = patience # how long to record video after motion detected
		self.annotate = annotate # if true add bounding rectangle to video feed
		self.move_time = None # time of move if move in last patience seconds, else none
		self.cap = cv.VideoCapture(cam_idx)
		self.img = self.cap.read()[1]
		self.height, self.width, _ = self.img.shape
		self.gray = self.to_gray(self.img)
		self.codec = cv.VideoWriter_fourcc('M','J','P','G')
		if not os.path.exists('videos'): os.mkdir('videos') # folder to store videos

	def display_feeds(self):
		'''
		Diplay video feeds on screen
		'''
		cv.imshow('Main Feed', self.img)
		cv.imshow('Movement', self.delta)
		cv.imshow('Thresholded Movement', self.delta_thresh)

	def add_info(self):
		'''
		Add time, status (whether movement is detected) to video feed
		Also add bouding box around movement if annotate parameter is True
		'''
		cur_time = datetime.now().strftime('%I:%M:%S')
		cv.putText(self.img, cur_time, (10, self.height-10), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 1)
		text = 'Movement Detected' if self.hasMovement else 'No Movement'
		cv.putText(self.img, text, (10,20), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 1)
		if not self.annotate or not self.hasMovement: return
		(x,y,w,h) = cv.boundingRect(self.delta)
		cv.rectangle(self.img, (x,y), (x+w,y+h), (0,255,0), 2)

	def initialize_recorder(self):
		'''
		Begin saving videos to a file
		'''
		folder = 'videos/'+datetime.now().strftime('%I:%M:%S-%A%d%B%Y')+'/'
		os.mkdir(folder)
		del_name = folder+'delta.avi'
		del_thresh_name = folder+'delta_thresh.avi'
		img_name = folder+'feed.avi'
		self.delwriter = cv.VideoWriter(del_name, self.codec, self.fps, (self.width, self.height), isColor=False)
		self.delthreshwriter = cv.VideoWriter(del_thresh_name, self.codec, self.fps, (self.width, self.height), isColor=False)
		self.imgwriter = cv.VideoWriter(img_name, self.codec, self.fps, (self.width, self.height))
		self.move_time = time()

	def write_recorder(self):
		'''
		Write video frames to file
		'''
		self.delwriter.write(self.delta)
		self.delthreshwriter.write(self.delta_thresh)
		self.imgwriter.write(self.img)

	def update_recorder(self):
		'''
		Begin, continue, or stop saving video to file as necessary
		'''
		if self.hasMovement and self.move_time: # extend recording time
			self.move_time = time()
			self.write_recorder()
		elif self.hasMovement and not self.move_time: # begin writing frames to new video
			cur_time = datetime.now().strftime('%I:%M:%S')
			print(cur_time+' - Began recording.')
			self.initialize_recorder()
			self.write_recorder()
		elif not self.hasMovement and self.move_time: 
			if time() <= self.move_time + self.patience: # write frames to video
				self.write_recorder()
			else: 										# stop writing
				cur_time = datetime.now().strftime('%I:%M:%S')
				print(cur_time+' - Finished recording.\n')
				self.move_time = None

	def to_gray(self, img):
		'''
		Converts image to grayscale
		'''
		gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
		gray = cv.GaussianBlur(gray, (21,21), 0)
		return gray

	def get_delta(self):
		'''
		Compare current frame with frame immediately previous to it
		'''
		gray2 = self.to_gray(self.img)
		self.delta = cv.absdiff(self.gray, gray2)
		self.delta_thresh = cv.threshold(self.delta, self.thresh, 255, cv.THRESH_BINARY)[1]
		self.delta_thresh = cv.dilate(self.delta_thresh, None, iterations=3)
		self.hasMovement = bool(self.delta_thresh.sum())
		self.gray = gray2

	def run(self):
		'''
		Execute until user presses esc key
		'''
		k = cv.waitKey(10)
		while k != self.esc:
			self.img = self.cap.read()[1]
			self.get_delta()
			self.add_info()
			self.update_recorder()
			self.display_feeds()
			k = cv.waitKey(10)
		self.cap.release()

if __name__ == '__main__':
	agent = MotionDetector()
	agent.run()