import MS_ClockReader
import importlib
import time

'''
=========================================================================
CLOCK TEST FILE-this test file is not a 100% accurate in its FALSE (X) readings,
				for false readings, if you run the main file (MS_ClockReader)
				with the image that failed, aside from clock10/clock16/clock20/clock22, 
				which are examples of limitations, every other image should have more than 50% accuracy
				I am not sure why, I need to reload the ClockReader file often for it to keep working, it seems fine as of right now,
				but just incase you run it and get different results, that's why.
=========================================================================
'''
times = {'clock1.jpg': [10, 10],
'clock2.jpg': [10,11],
'clock3.jpg': [10,10],
'clock4.jpg': [1,50],
'clock5.jpg': [10,10],
'clock6.jpg': [10,10],
'clock7.jpg': [1,50],
'clock8.jpg': [1,50],
'clock9.jpg': [2,58],
'clock10.jpg': [10,10],
'clock11.jpg': [8,22],
'clock12.jpg': [12,12],
'clock13.jpg': [6,53],
'clock14.jpg': [10,10],
'clock15.jpg': [10,10],
'clock16.jpg': [9,5],
'clock17.jpg': [10,10],
'clock18.jpg': [10,25],
'clock19.jpg': [1,50],
'clock20.jpg': [10,10],
'clock21.jpg': [3,0],
'clock22.jpg': [6,10],
'clock23.jpg': [10,29],
'clock24.jpg': [1,50],
'clock25.jpg': [1,50],
'clock26.jpg': [3,0],
'clock27.jpg': [11,5],
'clock28.jpg': [3,39],
'clock29.jpg': [10,10],
'clock30.jpg': [10,8] }

totalCount = 0
totalSuccess = 0
numFiles = 30
loopsPerFile =10

errThresh = 5
for i in range(1, numFiles + 1):
	filename = 'clock' + str(i) +'.jpg'
	numSuccess = 0
	count = 0
	realHour =  times[filename][0]
	realMinute =  times[filename][1]
	print(filename, end="| ")

	while(count < loopsPerFile):
		count += 1
		totalCount += 1
		clocktime = MS_ClockReader.main(filename)
		if(clocktime is None):
			print('?', end="")
			continue

		# print(realHour," ", realMinute)
		# print(time)
		hour = clocktime[0]
		minutes = clocktime[1]

		if(hour == realHour and abs(minutes - realMinute) < errThresh):
			numSuccess += 1
			totalSuccess += 1
			print('Y', end="")
		else:
			print('X', end="")
			importlib.reload(MS_ClockReader)

	importlib.reload(MS_ClockReader)
	print(" | Accuracy: ", (round(numSuccess/count * 100)))