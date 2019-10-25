# MotionDetection

A cat detection system (more precisely, a motion detection system currently used for cat detection) implemented using openCV-python. 

### Inspiration/Use Case
Used to investigate my housemates' suspicions that a cat has been sneaking into our house in the early morning via our front door mail slot. 

### User Interface and What To Expect
Constantly displays the camera feed and a 'delta' feed, a black and white representation of movement in the environment.

When motion is detected, it begins saving both video feeds. The video feeds are saved until 30 seconds has passed without movement. The videos are saved to timestamped folders, and the camera feed video is annotated with the time and the status (whether motion is detected at each given moment). 

To safely exit the program, press the escape key while one of the two windows is selected. 

### Downloading and Running
Clone the repository and install the packages listed in requirements.txt. 

### Adapting to Your Machine
Runs smoothly on a ubuntu machine with built in camera. To run on another machine, it may be necessary to changed the following parameters in the MotionDetector object initialization:
- cam_idx to your system's camera index
- esc to your system's 'esc' key number
- fps to match the frame rate of your system's camera

### The Back End
Motion is detected by comparing each frame with the frame immediately before it. The frames are converted to grayscale, blurred with a Gaussian filter, and the element-wise absolute difference between frames is computed. A threshold (default=8) is applied to the result to map each value to 0 or 255. The resultant image is dilated for display purposes. If any of the resultant pixels are 255 then movement is detected.

### Acknowledgement
The use of Gaussian blurring for denoising, and dilation for display purposed were inpsired by [this](https://www.pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/) blog post. 
