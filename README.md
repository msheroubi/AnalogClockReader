# READING ANALOG CLOCK

MS_ClockReader contains the actual algorithm, to see the algorithm in action for each image, and to check individual images. ClockTest does not show the process in action

## Usage
1. If using MS_ClockReader, scroll down all the way to the bottom and set the 'clock.jpg' string to be the filename. OR To use imagegrab and screen record a portion of the screen with a clock on it:
Comment Out the line where:
	 `screen = cv2.imread(filename)`
and uncomment the line that grabs the screen where 
	`screen = ImageGrab.grab....`

2. If using clockTest, check that the clock's actual time is registered in the dictionary, and that the ClockReader is being reloaded, since there is a bug with the probabilistic hough transform, after a large number of consecutive runs on different images it becomes somewhat inaccurate. The results should be some what similiar to the Test Results file, if there is a big disparity, then double check the results manually using the MS_ClockReader file for the images that fail, using method 1.

## Algorithm

The approach taken in this project was to isolate the actual clock from the rest of the image,
identify the clock hands, and calculate the time according to their angles.

The method for doing this consists of six steps:
1. Isolate the clock from the rest of the image
2. Apply edge detection to the image
3. Use Hough transform to isolate watch hands
4. Calculate line angles
5. Compute the time

### 1. Isolate the clock from the rest of the image

Given an image of a clock, the image must first be isolate into the form that the program
wants. Hough Transform were used in the code. The purpose of this technique is to filter out
just the clock from a scene. This was done by finding the largest circle in a scene using
OpenCV’s HoughCircles function.

### 2. Apply edge detection on the image

Once the image from the clock is isolated, the program would begin the identification process
of the clock. For that, Canny (sobel) edge detection is the method implemented. We used
OpenCV’s Canny function with a lower threshold of 50, and a upper threshold of 200.

### 3. Use Hough transform to isolate watch hands
We used Probabilistic Hough Transform to get the lines of the isolated region of interest. We
filter out any lines where there aren’t any points near the center of the image. We ran this
step around 20 times, to make sure we did not miss any clock hands, where when a new line
was detected, if the angular difference between the current hand C and an existing hand A
was bigger than the angular difference between existing hands B and A , then set B = C.

### 4. Calculate line angles
After the program is able to filter and select down the lines to a list of candidates from the
clock. The next step is to tell what number each line (hand) is pointing at.
The method that was implemented into the program assumes the hours 12, 3, 6, 9 respectively
presents with 0 degrees, 90 degrees, 180 degrees and 270 degrees. This is done by getting the
tangent of x over y. Using the ‘atan2’ function on delta x and delta y of every line, angle in
degrees can be calculated of the line relative to the x axis. The angle is given in radians and is
then converted to degrees over the interval [-180, 180]. Then the range is shifted to be from
[0, 360].

### 5. Compute the time
Finally, the the time could be calculated by the given algorithm, that the shortest line would
represent hour, the longer line would be minutes, and later we can implement the second
hand longest line would be the second hand.

Algorithm
```
Minutes = round(angle_minute_hand / 6)
Seconds = round(angle_second_hand / 6)
Hours = (angle_hour_hand / 6) / 5 #Rounded Down to nearest integer
```

There are minor error and accuracy checks in the function, refer to the computeTime()
function in the code.

## Limitations
- Having logos, letters, lighting changes, or any lines that are not the clock-hands,  near the center of the 1lock.
- Assume clock hands are not the same length, s.t. len(Hour hand) < len(Minute hand)
- Can not handle images of clocks from sharp angles, this could be fixed in the future.
- Video frames have to be fed one at a time into the loop at the bottom, where the view of the clock does not change in the video.
- Large images take a longer time to process, and the reading is less accurate, in the future we can auto resize the input image.
- When calculating angular difference, it does not recognise that 359 is close to 0 degrees.
- Clock-hands should be straight lines.
