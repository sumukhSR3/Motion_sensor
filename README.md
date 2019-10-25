# MotionDetection

A motion detection system implemented using openCV-python. 

Constantly displays the camera feed and a 'delta' feed, a black and white representation of movement in the environment.

When motion is detected, it begins saving both video feeds. The video feeds are saved until 30 seconds has passed without movement. The videos are saved to timestamped folders, and the camera feed video is annotated with the time and the status (whether motion is detected at each given moment). 

Press the escape key at any time to safely exit the program. 

Runs smoothly on a ubuntu machine with built in camera. To run on another machine, it may be necessary to changed the following parameters in the MotionDetector object initialization:
- cam_idx to your system's camera index
- esc to your system's 'esc' key number
- fps to match the frame rate of your system's camera

Motion is detected by comparing each frame with the frame immediately before it. The frames are converted to grayscale, blurred with a Gaussian filter, and the element-wise absolute difference between frames is computed. A threshold (default=8) is applied to the result to map each value to 0 or 255. The resultant image is dilated for display purposes. If any of the resultant pixels are 255 then movement is detected.
