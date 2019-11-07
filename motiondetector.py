import os
from time import time
from datetime import datetime

import numpy as np
import cv2 as cv

__all__ = ['MotionDetector']

class MotionDetector():
	def __init__(
		self, FPS=30, ESC=27, THRESH=8, PATIENCE=30, 
		FRAME_COUNT=10, CAM_IDX=0, annotate=False
		):
		# system's escape key number
		self.ESC = ESC
		# changes in pixel intensity >= thresh are considered movement
		self.THRESH = THRESH
		# how long to record video after motion detected
		self.PATIENCE = PATIENCE
		# min number of consecutive frames to begin recording
		self.FRAME_COUNT = FRAME_COUNT
		# if true add bounding rectangle to video feed 
		self.annotate = annotate
		# time of move if move in last PATIENCE seconds, else none
		self.move_time = None
		# number of consecutive frames with motion
		self.move_count = 0
		self.memory = []
		self.cap = cv.VideoCapture(CAM_IDX)
		self.img = self.cap.read()[1]
		self.height, self.width, _ = self.img.shape
		self.gray = self.to_gray(self.img)
		self.codec = cv.VideoWriter_fourcc('M','J','P','G')
		if not os.path.exists('videos'): os.mkdir('videos')
		# frame rate at which to save video
		self.FPS = self.get_fps() if FPS is None else FPS

	def get_fps(self):
		num_frames = 60
		start_time = time()
		for _ in range(num_frames):
			self.cap.read()
		fps = round(num_frames/(time()-start_time))
		print('Your camera is running at '+str(fps)+' FPS. To reduce',
				'initalization time, set FPS to this value in the',
				'MotionDetector constructor\n')
		return fps

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
		Add bouding box around movement if annotate parameter is True
		'''
		cur_time = datetime.now().strftime('%I:%M:%S')
		text = 'Movement Detected' if self.move_count > 0 else 'No Movement'
		cv.putText(
			self.img, cur_time, (10, self.height-10), 
			cv.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 1
			)
		cv.putText(
			self.img, text, (10,20), 
			cv.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 1
			)
		if not self.annotate or self.move_count == 0:
			return
		(x,y,w,h) = cv.boundingRect(self.delta_thresh)
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
		self.delwriter = cv.VideoWriter(
			del_name, self.codec, self.FPS, 
			(self.width, self.height), isColor=False
			)
		self.delthreshwriter = cv.VideoWriter(
			del_thresh_name, self.codec, self.FPS, 
			(self.width, self.height), isColor=False
			)
		self.imgwriter = cv.VideoWriter(
			img_name, self.codec, self.FPS, 
			(self.width, self.height)
			)
		self.move_time = time()
		self.write_memory()

	def write_memory(self):
		for (img, delta, delta_thresh) in self.memory:
			self.imgwriter.write(img)
			self.delwriter.write(delta)
			self.delthreshwriter.write(delta_thresh)
		self.memory = []

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
		# extend recording time
		if self.move_count > 0 and self.move_time is not None: 
			self.move_time = time()
			self.write_recorder()
		# begin writing frames to new video
		elif self.move_count >= self.FRAME_COUNT and self.move_time is None:
			cur_time = datetime.now().strftime('%I:%M:%S')
			print(cur_time+' - Began recording.')
			self.initialize_recorder()
			self.write_recorder()
		# determine if recording should be stopped
		elif not self.move_count > 0  and self.move_time: 
			if time() <= self.move_time + self.PATIENCE:
				self.write_recorder()
			else: 
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
		self.delta_thresh = cv.threshold(
			self.delta, self.THRESH, 255, cv.THRESH_BINARY
			)[1]
		self.delta_thresh = cv.dilate(self.delta_thresh, None, iterations=3)
		self.gray = gray2

	def update_memory(self):
		# update number of consecutive frames with motion
		if self.delta_thresh.sum() > 0:
			self.memory.append((self.img, self.delta, self.delta_thresh))
			self.move_count += 1
		else:
			self.memory = []
			self.move_count = 0

	def run(self):
		'''
		Execute until user presses esc key
		'''
		usr_input = cv.waitKey(10)
		start_time = time()
		while usr_input != self.ESC:
			self.img = self.cap.read()[1]
			self.get_delta()
			self.add_info()
			self.update_memory()
			self.update_recorder()
			self.display_feeds()
			usr_input = cv.waitKey(10)
		self.cap.release()

if __name__ == '__main__':
	agent = MotionDetector(FPS=30)
	agent.run()