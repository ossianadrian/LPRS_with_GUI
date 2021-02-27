import globals
from math import sqrt, pow
import dlib
import cv2
import numpy as np
import easyocr
import os
import sys

# cascade haar classifier for cars
CAR_CASCADE_HAAR_CLASSIFIER = cv2.CascadeClassifier('/home/ossi/Documents/licenta/graphical-user-interface/gui-app-lpr/engine/car_haar_classifier.xml')
# import video
input_video_path = sys.argv[1]
VIDEO = cv2.VideoCapture(input_video_path)


def calculateSpeed(point1, point2, FPS, PPM):
    # sqrt( (p2.a - p1.a)^2 + (p2.b - p1.b)^2 )
    distance_in_pixels = sqrt(pow(point2[0] - point1[0], 2) + pow(point2[1] - point1[1], 2))
    distance_in_meters = distance_in_pixels / PPM
    # return the speed calculated in km/h
    return distance_in_meters * FPS * globals.MS_KMPH

def calculateAverageSpeed(entryFrame, exitFrame, FPS ,distanceBetweenThe2Points):
    number_of_frames = exitFrame - entryFrame
    time = number_of_frames / FPS
    speed = distanceBetweenThe2Points / time
    return speed * globals.MS_KMPH

def calculateLineEcuation(P, Q):
    # the final ecuation will be ax + by = c 
    # stored in globals
    globals.A = Q[1] - P[1]
    globals.B = P[0] - Q[0]
    globals.C = globals.A * (P[0]) + globals.B * (P[1])


def calculateLineEcuationForLowerLine(P, Q):
    # the final ecuation will be ax + by = c 
    # stored in globals
    globals.A2 = Q[1] - P[1]
    globals.B2 = P[0] - Q[0]
    globals.C2 = globals.A2 * (P[0]) + globals.B2 * (P[1])

# **works only if P is to the left and under the Q
def checkIfPointIsBelowLine(a, b, c, thePoint):

    y_on_line = (c - a * thePoint[0] ) / b
    #check if the y of thePoint is smaller than y of the intersation with the line. If so, the point is below the line
    if thePoint[1] >= y_on_line:
        return True
    else:
        return False



def configureYoloV3():
    
    # read file with classes that yolov3 recognizes
    with open(globals.classesFile, 'rt') as f:
        globals.classNames = f.read().rstrip('\n').split('\n')
    # read the conf file and weights of yolov3
    modelConfiguration = '/home/ossi/Documents/licenta/graphical-user-interface/gui-app-lpr/engine/yolov3_LPR.cfg'
    modelWeights = '/home/ossi/Documents/licenta/graphical-user-interface/gui-app-lpr/engine/yolov3_LPR.weights'
    
    globals.net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
    globals.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    globals.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)    
    

def extractLicensePlate(img):
    blob = cv2.dnn.blobFromImage(img, 1/255, (globals.whT, globals.whT), [0,0,0], 1, crop = False)
    globals.net.setInput(blob)
    
    layerNames = globals.net.getLayerNames()
    # print(layerNames)
    globals.net.getUnconnectedOutLayers()
    outputNames = [layerNames[i[0]-1] for i in globals.net.getUnconnectedOutLayers()]
    # get the output of the 3 layers. Outputs is a list
    outputs = globals.net.forward(outputNames)
    
    #find objects in picture
    hT, wT, cT = img.shape
    # list with x,y,w,h
    bbox = []
    classIds = []
    # confidence values
    confs = []
    for output in outputs:
        for det in output:
            scores = det[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if confidence > globals.confThreshHold:
                w, h = int(det[2] * wT), int(det[3] * hT)
                x, y = int(det[0] * wT - w/2), int(det[1] * hT - h/2)
                bbox.append([x,y,w,h])
                classIds.append(classId)
                confs.append(float(confidence))
    indices = cv2.dnn.NMSBoxes(bbox, confs, globals.confThreshHold, globals.nmsThreshHold)
    x, y, w, h = 0, 0, 0, 0
    for i in indices:
        i = i[0]
        box = bbox[i]
        x, y, w, h = box[0], box[1], box[2], box[3]
        # return coordinates, confidence and "vehicle registration plate"
        return x, y, w, h, confs[i], globals.classNames[classIds[i]].upper()
        # cv2.rectangle(img, (x,y), (x+w, y+h), (0, 255, 0), 2)
        # cv2.putText(img, f'{globals.classNames[classIds[i]].upper()} {int(confs[i] * 100)}%' , (x, y-10), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0,255,0), 2)
    return 0,0,0,0,0,0



def trackCars():

    # create a file in which to write the output video
    output_video = cv2.VideoWriter('outputVideo.avi', cv2.VideoWriter_fourcc('M','J','P','G'), 20, (globals.WIDTH, globals.HEIGHT))
    current_car_id = 0
    frame_cnt = 0
    # get the fps of the video
    globals.FPS = VIDEO.get(cv2.CAP_PROP_FPS)

    #define lists for calculating the avg speed between 2 lines
    frameOfEntryPoint = [None] * 1000
    frameOfExitPoint = [None] * 1000
    cars_under_first_line = [None] * 1000
    cars_under_second_line = [None] * 1000
    


    car_tracker_dict = {}
    cars_point1 = {}
    cars_point2 = {}
    speed_of_cars = [None] * 1000
    extracted_cars = [None] * 1000
    license_plate_numbers = [None] * 1000

    #define path for exporting pictures
    img_folder_path = '/home/ossi/Documents/licenta/graphical-user-interface/gui-app-lpr/engine/exported'

    # calculate ecuation for the line determined by 2 stable points. Only vehicles passing this line will get the speed registered
    calculateLineEcuation(globals.START_POINT_LIST, globals.END_POINT_LIST)
    calculateLineEcuationForLowerLine(globals.START_POINT_LIST2, globals.END_POINT_LIST2)
    # preconfigure yoloV3 - only once
    print("Configuring yolov3...")
    configureYoloV3()
    # configure reader - only once
    print("Loading easyOCR")
    reader = easyocr.Reader(['en'])

    print("Beginning processing the video")

    while True:

        if cv2.waitKey(33) == 27:
            break

        ret, image_from_video = VIDEO.read()
        # Count current frame
        frame_cnt = frame_cnt + 1

        # create a copy of the 4k image
        original_image_4k = image_from_video

        # if video is over, break
        if type(image_from_video) == type(None):
            print("Video Finished!")
            break

        image_from_video = cv2.resize(image_from_video, (globals.WIDTH, globals.HEIGHT))
        modified_image = image_from_video.copy()
        # A list of cars to delete from array. In this list IDs are stored
        cars_to_delete = []

        # Check if any car has left the field of view
        for car in car_tracker_dict.keys():
            #Update the tracking accuracity
            tracker_accuracity = car_tracker_dict[car].update(image_from_video)
            if tracker_accuracity < 4:
                cars_to_delete.append(car)

        for car in cars_to_delete:
            print('[Remove] Deleting car with id = ' + str(car))
            sys.stdout.flush()
            # additional argument None needed in case a car is not present in the tracker. Otherwise we get an exception thrown
            car_tracker_dict.pop(car, None)
            cars_point1.pop(car, None)
            cars_point2.pop(car, None)

        #do all these checks each 10 frames

        if frame_cnt % 10 == 0:
            #convert image to grayscale
            grayscale_image = cv2.cvtColor(image_from_video, cv2.COLOR_BGR2GRAY)
            # use classifier to detect cars
            cars_detected = CAR_CASCADE_HAAR_CLASSIFIER.detectMultiScale(grayscale_image, 1.1, 13, 18, (24, 24))
            
            for (int32_x, int32_y, int32_w, int32_h) in cars_detected:
                #cast to integer python
                x, y, w, h = int(int32_x), int(int32_y), int(int32_w), int(int32_h)

                # calculate the center of gravity for the rectangle that fits the car
                x_center = x + w * 0.5
                y_center = y + h * 0.5

                matched_car = None
                # detect if car is already found in dictionary
                for car in car_tracker_dict.keys():
                    car_position = car_tracker_dict[car].get_position()

                    tracked_x, tracked_y, tracked_w, tracked_h = int(car_position.left()), int(car_position.top()), int(car_position.width()), int(car_position.height())

                    # calculate the center of gravity for the rectangle in which the tracked car is located
                    tracked_x_center = tracked_x + tracked_w * 0.5
                    tracked_y_center = tracked_y + tracked_h * 0.5

                    # if the center of gravity for the first tracked car is in range of the one calculated from above, then it's a match

                    if (tracked_x <= x_center <= (tracked_x + tracked_w)) and (tracked_y <= y_center <= (tracked_y + tracked_h)) and (x <= tracked_x_center <= (x+w)) and (y <= tracked_y_center <= (y+h)):
                        matched_car = car
                        break

                if matched_car is None:
                    print('[Added car] Creating new tracker for car with id = ' + str(current_car_id))
                    sys.stdout.flush()
                    # Create a correlation tracker to track the new identified car in each frame of the video
                    correlation_tracker = dlib.correlation_tracker()
                    correlation_tracker.start_track(image_from_video, dlib.rectangle(x, y, x+w, y+h))
                    car_tracker_dict[current_car_id] = correlation_tracker
                    # Save the first point used for calculating speed
                    cars_point1[current_car_id] = [x, y, w, h]
                    current_car_id = current_car_id + 1

            # do this code for all the cars present in the dictionary
        for car in car_tracker_dict.keys():
            car_position = car_tracker_dict[car].get_position()
            tracked_x, tracked_y, tracked_w, tracked_h = int(car_position.left()), int(car_position.top()), int(car_position.width()), int(car_position.height())

            # draw a rectangle on the image to identify the car visually
            cv2.rectangle(modified_image, (tracked_x, tracked_y), (tracked_x + tracked_w, tracked_y + tracked_h), (0, 0 , 255), 2)

            # Add point 2 for this car for speed estimation 
            cars_point2[car] = [tracked_x, tracked_y, tracked_w, tracked_h]


        for i in cars_point1.keys():

            [x1, y1, w1, h1] = cars_point1[i]
            [x2, y2, w2, h2] = cars_point2[i]

            if cars_point1[i] != cars_point2[i]:
                x_center = x1 + w1 * 0.5
                y_center = y1 + h1 * 0.5

                # calculate the speed only if the car passed the point 275 450 and the speed is 0 or None
                # if (speed_of_cars[i] == 0 or speed_of_cars[i] == None) and y1 >= 275 and y1 <= 450:

                # modified_image = cv2.line(modified_image, (int(x_center), int(y_center)), END_POINT, (0,0,255), 9)
                if (speed_of_cars[i] == 0 or speed_of_cars[i] == None) and checkIfPointIsBelowLine(globals.A, globals.B, globals.C, [x2+w2, y2+w2]) and cars_under_first_line[i] == None:
                    #store initial frame_cnt for enter, and the frame for exit
                    frameOfEntryPoint[i] = frame_cnt
                    print('[Entry point] The car with id = ' + str(i) + ' has entered the speed calculation zone')
                    sys.stdout.flush()
                    cars_under_first_line[i] = 1
                    # speed_of_cars[i] = calculateSpeed(cars_point1[i], cars_point2[i], globals.FPS ,globals.PPM)
                if (speed_of_cars[i] == 0 or speed_of_cars[i] == None) and checkIfPointIsBelowLine(globals.A2, globals.B2, globals.C2, [x2+w2, y2+w2]) and cars_under_second_line[i] == None:
                    frameOfExitPoint[i] = frame_cnt
                    print('[Exit point] The car with id = ' + str(i) + ' has exited the speed calculation zone')
                    sys.stdout.flush()
                    speed_of_cars[i] = calculateAverageSpeed(frameOfEntryPoint[i], frameOfExitPoint[i], globals.FPS, globals.distanceBetweenThe2Lines)
                    cars_under_second_line[i] = 1


                if speed_of_cars[i] != None :
                    cv2.putText(modified_image, "Car[" + str(i) + "] " + str(int(speed_of_cars[i])) + "km/h", (int(x1 + w1/2), int(y1-8)), 3 , 0.6 , (255, 255, 255), 2)
                    if license_plate_numbers[i] != None:
                        cv2.putText(modified_image, license_plate_numbers[i], (int(x1 + w1/2), int(y1-32)), 3 , 0.6 , (255, 255, 255), 2)

                    # if car hasn't been recognized, proceed forward with license plate detection
                    if extracted_cars[i] == None:
                        print('[LPR] Preparing image for LPR for car with id = ' + str(i) + ' having the speed = ' + str(int(speed_of_cars[i])) + 'km/h')
                        sys.stdout.flush()
                        # cv2.imwrite('ExtractedImageForLPR' + str(i) + '.png', image_from_video[y2:(y2 + h2), x2:(x2 + w2)])
                        # get a more detailed image from original 4k footage. Scale accordingly
                        cropped_image_4k = original_image_4k[int(y2*globals.IMG_720p_TO_2160p):(int(y2*globals.IMG_720p_TO_2160p) + int(h2*globals.IMG_720p_TO_2160p)), int(x2*globals.IMG_720p_TO_2160p):(int(x2*globals.IMG_720p_TO_2160p) + int(w2*globals.IMG_720p_TO_2160p))]
                        # this is when working with fHD footage
                        # cropped_image_4k = image_from_video[y2:(y2 + h2), x2:(x2 + w2)]
                        
                        # extract license plate location
                        x_vrp, y_vrp, w_vrp, h_vrp, confidence, type_of_object_detected = extractLicensePlate(cropped_image_4k)
                        if x_vrp != 0:
                            print('[LPR] License plate position detected for car with id = ' + str(i) )
                            sys.stdout.flush()
                            # draw rectangle to highlight license plate
                            cv2.rectangle(cropped_image_4k, (x_vrp, y_vrp), (x_vrp + w_vrp + 7, y_vrp + h_vrp + 7), (0, 255 , 0), 2)
                            cropped_license_plate = cropped_image_4k[y_vrp:y_vrp+h_vrp+7, x_vrp:x_vrp+w_vrp+7]
                            # read text from image
                            result_from_easyOCR = reader.readtext(cropped_license_plate)
                            actual_license_plate_number = result_from_easyOCR[0][-2]
                            confidence_license_plate_number = result_from_easyOCR[0][-1]
                            license_plate_numbers[i] = actual_license_plate_number
                            print('[LPR] Vehicle registration number detected [' + actual_license_plate_number + ']' + ' for car with id = ' + str(i) )
                            sys.stdout.flush()
                            # put info on image
                            cv2.putText(cropped_image_4k, actual_license_plate_number + " " + str(int(confidence_license_plate_number * 100)) + "%", (x_vrp, y_vrp-8), cv2.FONT_HERSHEY_SIMPLEX , 0.6 , (0, 255, 0), 1)
                            cv2.putText(cropped_image_4k, str(type_of_object_detected) + " " + str(int(confidence*100)) + "%", (x_vrp - 40, y_vrp+50), cv2.FONT_HERSHEY_SIMPLEX , 0.3 , (0, 255, 0), 1)
                            cv2.putText(cropped_image_4k, "Car[" + str(i) + "] " + str(int(speed_of_cars[i])) + "km/h", (x_vrp, y_vrp-32), cv2.FONT_HERSHEY_SIMPLEX , 0.6 , (0, 255, 0), 1)
                            cv2.imwrite(os.path.join(img_folder_path,'resulted_image_with_LPR' + str(i) + '.png'), cropped_image_4k)
                            # cv2.imwrite(os.path.join(img_folder_path, 'img_sample' + str(i) + '.png'), image_from_video) 
                        extracted_cars[i] = 1



            cars_point1[i] = cars_point2[i]

        cv2.line(modified_image, globals.START_POINT, globals.END_POINT, (0,0,255), 2)
        cv2.line(modified_image, globals.START_POINT2, globals.END_POINT2, (0,0,255), 2)
        cv2.line(modified_image, globals.START_POINT, globals.START_POINT2, (0,0,255), 2)
        cv2.line(modified_image, globals.END_POINT, globals.END_POINT2, (0,0,255), 2)
        cv2.imshow('modified image', modified_image)

        if cv2.waitKey(33) == ord('c'):
            cv2.imwrite(os.path.join(img_folder_path,'captured_image_from_keyboard.png'), modified_image)

        
        # Write output image to the new video file
        # output_video.write(modified_image)

    cv2.destroyAllWindows()

def dosmth():
    i = 0
    while i < 100:
        i = i + 1
        print(i)

if __name__ == '__main__':
    # dosmth()
    print("Begin")
    trackCars()
    print("Finished")
