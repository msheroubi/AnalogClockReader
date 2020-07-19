import numpy as np
import cv2
import math
from PIL import ImageGrab
import time
from skimage.transform import (hough_line, hough_line_peaks,
                               probabilistic_hough_line)
from skimage.feature import canny
from skimage import data

""" 
============================================================================================================
READING TIME OFF ANALOG CLOCKS FROM IMAGES/VIDEO

Video frames have to be fed one at a time into the loop at the bottom, where the view of the clock does not change in the video.
'###' signifies deprecated/old code used
============================================================================================================

"""

## prevRoi: used to store previous ROI incase the roi detection fails, during the loop, it uses the previous ROI which should be the clock
prevRoi = [[0,0],[1,0],[1,1],[0,1]]

clockCenter = (0,0)

## glob_* : used to store properties of the clockhands
glob_clockhands = [[], []]
glob_lineCoords = [(), ()];

## DEPRECATED
##As of April 2nd, this wasn't used. This was used to draw lines when using OpenCv's Hough Lines
def draw_lines(img, lines):
    try:
        for line in lines:
            coords = line[0]
            return cv2.line(img,(coords[0], coords[1]), (coords[2], coords[3]), [255,255,255], 3)
    except:
        pass
           

##Get region of interest given an image and vertices and returns a masked image where anywhere outside the ROI is black
def roi(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    masked = cv2.bitwise_and(img, mask)
    return masked

## DEPRECATED
##As of April 2nd, this wasn't used. This was used to generate automatic threshholds for an image using a sigma value and the median of the image array
def auto_canny(image, sigma=0.33):
    #Get median
    v = np.median(image)

    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)

    return edged

## BULK OF IMAGE PROCESSING
## Takes an input image, retrieves the ROI, get clock hands, store properties of clockhands in global variables glob_lineCoords & glob_clockhands, return image with lines on it
##   -This process is run a few times to make sure the probabilistic huogh transform gets both clock hands
def process_img(original_image):
    #See top for var explanations
    global prevRoi
    global clockCenter
    global glob_lineCoords
    global glob_clockhands

    processed_img = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    output = original_image.copy()


    # detect circles in the image
    circles = cv2.HoughCircles(processed_img, cv2.HOUGH_GRADIENT, 1.1, 100, maxRadius=300)

    #Dimensions of ROI
    roiDim = [] 

    # ensure at least some circles were found
    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")
     
        # loop over the (x, y) coordinates and radius of the circles
        maxR = 0
        for (x, y, r) in circles:
            # draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
            cv2.circle(output, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
            clockCenter=(x,y)
            if(r > maxR):
                roiDim = [[x-r-5, y-r-5], [x+r+5, y-r-5], [x+r+5, y+r+5],[x-r-5, y+r+5]]
                prevRoi = roiDim
    
    if len(roiDim) == 0:
        roiDim = prevRoi

    ##-----------------DEPRECATED
    ###kernel = np.ones((3,3),np.uint8)
    ###processed_img = cv2.erode(processed_img,kernel,iterations = 1)
    ###processed_img = auto_canny(processed_img)
    ###processed_img = cv2.GaussianBlur(processed_img, (3, 3), 0)
    ###edges = cv2.Canny(processed_img,50, 150, apertureSize=3)
    ###edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    #see ROI notes in notebook
    vertices = np.array(roiDim)
    processed_img = roi(processed_img, [vertices])
    

    minLineLength = 50
    maxLineGap = 3



    #each hand has a x0,x1,y0,y1 and an angle where 0 is hours, 1 is minutes, 2 is seconds

    edges = cv2.Canny(processed_img, 50, 200)
    ###edges = auto_canny(processed_img)

    kernel = np.ones((6,6),np.uint8)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    ###edges = cv2.morphologyEx(edges, cv2.MORPH_OPEN, np.ones((2,2), np.uint8))

    lines = probabilistic_hough_line(edges, threshold=5, line_length=minLineLength, line_gap=maxLineGap)

    ##------------------DEPRECATED
    ###lines = cv2.HoughLines(edges, 1, np.pi/180, 60)
    ###lines = cv2.HoughLinesP(edges, 1, np.pi/180, 60, minLineLength, maxLineGap)
    #clockhands = [[(0,0), (1,1), np.pi], [(0,0), (q1,1), np.pi], [(0,0), (1,1), np.pi]]
    #maxLine = 0
    #minLine = 1000

    lineCoords = [[]]
    x, y = clockCenter
    lineAngs = []
    newAng = True
    maxima1 = 0
    maxima2 = 0

    #Placeholder for blob detection, checks if root of line is within a set distance of the center
    distCenter = 15


    ###clockhands = [0, 0]
    if lines is not None:
        for line in lines:
            ### for x1,y1,x2,y2 in line:        #For OpenCv's HoughLinesP
            p0, p1 = line
            x1, y1 = p0
            x2, y2 = p1

            #Makes the point closest to the center is x1 y1
            if(abs(y2 - y) < abs(y1 - y) and abs(x2-x) < abs(x1-x)):
                temp = x1
                x1 = x2
                x2 = temp
                temp = y1
                y1 = y2
                y2 = temp
                

            lenLine = ((x2-x1) ** 2 + (y2-y1) ** 2) ** 0.5

            if(((abs(x-x1) < distCenter and abs(y-y1) < distCenter) or (abs(x-x2) < distCenter and abs(y-y2) < distCenter)) and lenLine > minLineLength):
                lineCoords.append([(x1,y1), (x2,y2)])
                
                ###ang = np.arctan2((y1-y2),(x2-x1))

                #Bottom of screen = max(y), rotate unit circle to match the clock
                ang = np.arctan2((x2-x1),(y1-y2))
                ang = ang * 180 / math.pi
                ang = (ang + 360) % 360         #Convert angle to extend range from [-180, 180] to [0, 360]

                #Check if angle of line is already stored
                for lineAng in lineAngs:
                    if(abs(ang- lineAng) <= 5):    #use 5, since 6 degrees is one tick on the clock
                        newAng = False      #Keep False

                ## -------------------DEPRECATED
                ### if(lenLine > maxima1 and newAng):
                ###     maxima1 = lenLine
                ###     clockhands[0] = ang
                ### elif(lenLine > maxima2 and newAng):
                ###     maxima2 = lenLine
                ###     clockhands[1] = ang


                #Checks if angle is a new angle
                if(newAng):
                    lineAngs.append(ang)                           
                    cv2.line(original_image,(x1,y1),(x2,y2),(0,0,255),2) #Draw line

                ##If ClockHands are empty, and angles are different from existing angles, save line properties
                if(len(glob_clockhands[0]) == 0):
                    glob_clockhands[0] = [ang, lenLine]
                    glob_lineCoords[0] = [(x1,y1), (x2,y2)]
                elif(len(glob_clockhands[1]) == 0):
                    if(abs(ang - glob_clockhands[0][0]) > 10):
                        glob_clockhands[1] = [ang, lenLine]
                        glob_lineCoords[1] = [(x1,y1), (x2,y2)]
                else:
                    #If both clockhand slots are full, check if the angular difference between the current angle is bigger than the other two, replace with the bigger angular difference
                    if(abs(ang - glob_clockhands[0][0]) > abs(glob_clockhands[0][0] - glob_clockhands[1][0]) + 5 and abs(ang - glob_clockhands[0][0]) < 350):
                        glob_clockhands[1] = [ang, lenLine]
                        glob_lineCoords[1] = [(x1,y1), (x2,y2)]
                    elif(abs(ang - glob_clockhands[1][0]) > abs(glob_clockhands[1][0] - glob_clockhands[0][0]) + 5 and abs(ang - glob_clockhands[0][0]) < 350):
                        glob_clockhands[0] = [ang, lenLine]
                        glob_lineCoords[0] = [(x1,y1), (x2,y2)]
                    elif(abs(ang - glob_clockhands[0][0]) < abs(glob_clockhands[0][0] - glob_clockhands[1][0]) + 5):
                        if(lenLine > glob_clockhands[1][1] and (abs(ang - glob_clockhands[1][0]) < 10 or abs(ang - glob_clockhands[1][0]) > 350)):
                            glob_clockhands[1] = [ang, lenLine]
                            glob_lineCoords[1] = [(x1,y1), (x2,y2)]
                    elif(abs(ang - glob_clockhands[1][0]) < abs(glob_clockhands[1][0] - glob_clockhands[0][0]) + 5):
                        if(lenLine > glob_clockhands[0][1] and (abs(ang - glob_clockhands[0][0]) < 10 or abs(ang - glob_clockhands[0][0]) > 350)):
                            glob_clockhands[0] = [ang, lenLine]
                            glob_lineCoords[0] = [(x1,y1), (x2,y2)]


                    ##-----------------------------------------DEPRECATED
                    # elif(newAng):
                    # #If both clockhand slots are full, check if the angular difference between the current angle is bigger than the other two, replace with the bigger angular difference
                    # if(abs(ang - glob_clockhands[0][0]) > abs(glob_clockhands[0][0] - glob_clockhands[1][0]) + 5 and abs(ang - glob_clockhands[0][0]) < 350):
                    #     glob_clockhands[1] = [ang, lenLine]
                    #     glob_lineCoords[1] = [(x1,y1), (x2,y2)]
                    # elif(abs(ang - glob_clockhands[1][0]) > abs(glob_clockhands[1][0] - glob_clockhands[0][0]) + 5 and abs(ang - glob_clockhands[1][0]) < 350):
                    #     glob_clockhands[0] = [ang, lenLine]
                    #     glob_lineCoords[0] = [(x1,y1), (x2,y2)]
                    # elif(abs(ang - glob_clockhands[0][0]) < abs(glob_clockhands[0][0] - glob_clockhands[1][0]) + 5 and abs(ang - glob_clockhands[0][0]) < 350):
                    #     if(lenLine > glob_clockhands[1][1]):
                    #         glob_clockhands[1] = [ang, lenLine]
                    #         glob_lineCoords[1] = [(x1,y1), (x2,y2)]
                    # elif(abs(ang - glob_clockhands[1][0]) < abs(glob_clockhands[1][0] - glob_clockhands[0][0]) + 5 and abs(ang - glob_clockhands[1][0]) < 350):
                    #     if(lenLine > glob_clockhands[0][1]):
                    #         glob_clockhands[0] = [ang, lenLine]
                    #         glob_lineCoords[0] = [(x1,y1), (x2,y2)]  
                    ### else:
                        ### for i in range(0, len(glob_clockhands)):
                        ###     if(abs(abs(glob_clockhands[i][0]) - abs(ang))>5)


            ##------------------DEPRECATED
            # for rho,theta in line:        #For OpenCv's HoughLines
            #     a = np.cos(theta)
            #     b = np.sin(theta)

            #     x0 = a*rho
            #     y0 = b*rho
            #     x1 = int(x0 + 1000*(-b))
            #     y1 = int(y0 + 1000*(a))
            #     x2 = int(x0 - 1000*(-b))
            #     y2 = int(y0 - 1000*(a))

            #     lenLine = ((x2-x1) ** 2 + (y2-y1) ** 2) ** 0.5
            #     if(abs(x-x1) < 25 and abs(y-y1) < 25):
            #         cv2.line(processed_img,(x1,y1),(x2,y2),(0,255,0),2)

    ##----------------------DEPRECATED
    #kernel = np.ones((5,5),np.uint8)
    #edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel )
    #lines = cv2.HoughLinesP(edges, 1, np.pi/180,10,100, minLineLength, maxLineGap)
    #newIm = draw_lines(np.zeros(processed_img.shape), lines)

    return original_image

##Compute time based on angles and return time in a list of the form [HH, mm, ss]
def computeTime(ang_H, ang_M, ang_S=0):
    mm = round(abs(ang_M) / 6)
    ss = round(abs(ang_S) / 6)
    errHH = round((abs(ang_H) / 6) /5)   #Hours, rounded normally, used to check the hours reading is accurate
    HH = (abs(ang_H) / 6) // 5       #Floored down to the nearest integer

    if(ss == 60):
        mm += 1
        ss = 0
    if(mm == 60):
        HH += 1
        mm = 0
    elif(mm < 30 and (errHH != HH)):    #Checks if the errH is rounded up while HH is rounded down and minutes are < 30 minutes,
                                            # if so, then the reading is inaccurate and we need to increment HH by 1
        HH += 1
    elif(mm>45 and (errHH == HH)):      #Checks if the angle for the hour hand may have been misread as the next hour
        HH += -1
    if(HH <= 0):
        HH = 12 + HH

    ###return [int(HH), int(mm), int(ss)]
    return [int(HH), int(mm)]

#Convert time from previous function into a string of the form HH:mm:ss
def timeToString(temp):
    for i in range(0, len(temp)):
        temp[i] = str(temp[i])

    return ":".join(temp)

def main(imname):
    last_time = time.time()
    count = 0
    screen = None
    numIterations = 20
    while(count < numIterations):
        count += 1
        """
        ------------------------------------------------------------------------------
        $CHOOSE IMAGE INPUT HERE$
        Set screen to be input image; imread, ImageGrab, etc...
        Feed it one frame at a time

        """
        #screen = ImageGrab.grab(bbox=(0, 100, 750, 600))               #x, y, w , h | Screen capture input
        #runBool = True
        screen = cv2.imread(imname)
        if(screen is None):
            print('File Not Found')
            return

        ###screen_np= cv2.resize(np.array(screen), (960,540))
        screen_np = np.array(screen)
        new_screen = process_img(screen_np)

        #print('Loop took {} seconds'.format(time.time() -last_time))
        #last_time = time.time()
        if __name__ == '__main__':
            try:
                cv2.imshow('window', new_screen)
            except:
                print("Imshow error")
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break

    #Show final image with lines on it
    screen_np = np.array(screen)
    original_image = screen_np.copy()
    #print(glob_clockhands)
    if(len(glob_clockhands[1]) ==0):
        if __name__ == '__main__':
            print("Could not detect all clock hands")
    else:   
        for line in glob_lineCoords:
            cv2.line(screen_np,line[0],line[1],(0,0,255),2)

        ang_H = 0
        ang_M = 0
        if(glob_clockhands[0][1] > glob_clockhands[1][1]):
            ang_H = glob_clockhands[1][0]
            ang_M = glob_clockhands[0][0]
        else:
            ang_H = glob_clockhands[0][0]
            ang_M = glob_clockhands[1][0]

        clocktime = computeTime(ang_H, ang_M)
        if __name__ == '__main__':
            print(timeToString(clocktime))

        if not __name__ == '__main__':    
            return clocktime

    #---USE THIS TO VIEW OUTPUT OF THE IMAGE
    if __name__ == '__main__':
        final = np.concatenate((original_image, screen_np), axis=1)
        try:
            cv2.imshow('window', final)
        except:
            print("Imshow error")
        cv2.waitKey()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main('clock20.jpg')