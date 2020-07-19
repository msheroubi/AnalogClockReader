# READING ANALOG CLOCK

MS_ClockReader contains the actual algorithm, to see the algorithm in action for each image, and to check individual images. ClockTest does not show the process in action

## Usage
1. If using MS_ClockReader, scroll down all the way to the bottom and set the 'clock.jpg' string to be the filename. OR To use imagegrab and screen record a portion of the screen with a clock on it:
Comment Out the line where:
	 `screen = cv2.imread(filename)`
and uncomment the line that grabs the screen where 
	`screen = ImageGrab.grab....`

2. If using clockTest, check that the clock's actual time is registered in the dictionary, and that the ClockReader is being reloaded, since there is a bug with the probabilistic hough transform, after a large number of consecutive runs on different images it becomes somewhat inaccurate. The results should be some what similiar to the Test Results file, if there is a big disparity, then double check the results manually using the MS_ClockReader file for the images that fail, using method 1.

## Limitations
- Having logos, letters, lighting changes, or any lines that are not the clock-hands,  near the center of the 1lock.
- Assume clock hands are not the same length, s.t. len(Hour hand) < len(Minute hand)
- Can not handle images of clocks from sharp angles, this could be fixed in the future.
- Video frames have to be fed one at a time into the loop at the bottom, where the view of the clock does not change in the video.
- Large images take a longer time to process, and the reading is less accurate, in the future we can auto resize the input image.
- When calculating angular difference, it does not recognise that 359 is close to 0 degrees.
- Clock-hands should be straight lines.
