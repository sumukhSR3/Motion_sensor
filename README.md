# MotionDetection

A cat detection system (a motion detection system currently used for cat detection) implemented using openCV-python. 

### Inspiration/Use Case
Used to investigate my housemates' suspicions that a cat has been sneaking into our house in the early morning via our front door mail slot. 

### User Interface and What To Expect
Constantly displays the camera feed and two 'delta' feeds, both being grayscale representations of movement in the environment. The first delta feed's pixels are given by the absolute difference in intensity between each frame, so faster movement gives higher intensity pixels. The second is that feed converted to black and white by thresholding with the `THRESH` parameter (default 8). 

When motion is detected for `FRAME_COUNT` (default 5) consecutive frames, it begins saving the three video feeds. These are saved until `PATIENCE` seconds (default 30) have passed without movement. The videos are saved to timestamped folders, and the camera feed video is annotated with the time and the status (whether motion is detected at each given moment). 

To safely exit the program, press the escape key while one of the windows is selected. 

### Downloading and Running
Clone the repository and install the packages listed in requirements.txt. 

### Adapting to Your Machine
Runs smoothly on a ubuntu machine with built in camera. To run on another machine, it may be necessary to changed the following constants in the MotionDetector object initialization:
- `CAM_IDX` to your system's camera index
- `ESC` to your system's 'esc' key number
- `FPS` to the frame rate of your camera

### Parameters / Constants to Change to Your Needs
- `THRESH` (default 8): the minimum change in pixel intensity required to be considered motion
- `PATIENCE` (default 30): the number of seconds to continue recording after the most recent motion
- `FRAME_COUNT` (default 5): the number of consecutive frames that must contain motion in order to begin recording. Note that consistent motion for `FRAME_COUNT` frames is equivalent to consistent motion for `FRAME_COUNT / FPS` seconds
-  `annotate` (default False): whether or not to place a bounding box around the motion in the main video feed. Interesting but can make the video feel cluttered

### The Back End
Motion is detected by background subtraction, in which the difference between each consecutive frame is calculated and studied. The frames are converted to grayscale, blurred with a Gaussian filter, and the element-wise absolute difference between frames is computed. The threshold is applied to the result to map each value to 0 or 255. The resultant image is dilated for display purposes. If any of the resultant pixels are 255 then movement is detected. When movement is detected while not yet recording, each consecutive frame with movement is appended to `memory`. Once there are at least `FRAME_COUNT` consecutive frames in memory, each of these frames is recorded and we begin real-time recording. If there is a frame without motion before `FRAME_COUNT` is reached, the memory is cleared and the process repeats.

### Notes
- This `memory` and `FRAME_COUNT` functionality were introduced to decrease the number of false positives that arised from flickering lights. Note that this functionality relies on the assumption that we are only interested in motions that begin with a consistent period of motion of at least `FRAME_COUNT / FPS` seconds. 

### References
The use of Gaussian blurring for denoising, and dilation for display purposed were inpsired by [this](https://www.pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/) blog post. 
