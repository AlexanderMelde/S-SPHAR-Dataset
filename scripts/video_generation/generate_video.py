"""
Generates videos based on image frames generated using the Unity simulation.

Expected input folder structure:

    UnityProjectFolder/rec/[recording_name]/
        _img/
            000000001.png
            000000002.png
        _layer/
            000000001.png
            000000002.png
        layer.json

Possible output modes that can be reangered in OUTPUT_VIDEO_MODES to define the
order of the split screen videos.

    - original      original images from _img folder
    - mask          segmentation mask images from _layer folder  
    - overlay       half-transparent overlay of masks over original images
    
    - black         just black, can be used as a spacing if you only want 3 videos in a 4-in-1 split.
    - oneclass      segmentation mask of only one specific class, specified in ONECLASS_CLASSNAME
    - bbox          original image with labeled bounding boxes around each action instance

Saves Video to the input folder using a file name of the form "output_[modes].mp4" generated
based on the chosen output modes. BBox Tubes will be saved to the subfolder defined in
VIDEO_TUBES_FOLDER and structured by class names, if SAVE_VIDEO_TUBES is set to True.

Author: Alexander Melde (alexander@melde.net)
"""


import os
import json
import glob
import warnings

import cv2
import imutils
import numpy as np
from tqdm import tqdm
import helper_functions as hf
from helper_classes import Instance, InstanceDB, InstanceFrameData, Tube

#---------------------#
#    CONFIGURATION    #
#---------------------#

# configure image frame path
BASE_FOLDER = "C:/Users/alexa/Documents/Unity Projects/Marketplace/rec"
RECORDING_FOLDER = 'sspha8_ActionSim_30fps'  # relative to BASE_FOLDER

# list of labels that are generated but should not be used for action classification
NO_ACTION_LABELS = ["Car", "Default", "UI", "Ground", "Water", "Lighting"]

FRAMERATE = 30
STOP_AFTER_FRAME = None  # either None or the maximum number of frames to process

# possible modes: ['mask', 'overlay', 'original' , 'black', oneclass, bbox]
OUTPUT_VIDEO_MODES = ['original', 'mask', 'overlay', 'bbox']
ONECLASS_CLASSNAME = 'kicking' # class to use for oneclass option

# use mp4 as a lossy codec (faster and with smaller filesize) instead of avi
USE_LOSSY = True

# Should it generate and save spatiotemporally cropped bbox tube videos?
SAVE_VIDEO_TUBES = True  # requires 'bbox' in OUTPUT_VIDEO_MODES


VIDEO_TUBES_FOLDER = 'tubes' # write tubes to this folder. relative to RECORDING_FOLDER
TUBE_PADDING = 50  # pixels to add to each side of the tube crops

# minimum frame number needed to save a tube
MIN_TUBE_LENGTH = 1 * FRAMERATE  # use n*FRAMERATE for n seconds

# configure imported warnings package
warnings.formatwarning = hf.warning_on_one_line


#---------------------#
#  SCRIPT EXECUTION   #
#---------------------#

#
# Read JSON metadata and images
#
print("Reading JSON Labels...")
with open(os.path.join(BASE_FOLDER, RECORDING_FOLDER, 'layer.json')) as layer_json_file:
    layer_json_data = json.load(layer_json_file)

name2color = {entry['name']: hf.rgb2bgr(hf.hex2rgb(entry['color'], True))
              for entry in tqdm(layer_json_data['labels'], desc="- labels  ", unit=" labels")}

# note that this can have less entries then name2color if colors are used for multiple label names:
color2name = {v: k for k, v in name2color.items()}

print("Reading image folders...")
has_read_first = False
folder_dict = {}
for subfolder in ['_layer', '_img']:
    img_array = []
    image_paths = sorted(glob.glob(os.path.join(
        BASE_FOLDER, RECORDING_FOLDER, subfolder, '*.png')))
    if STOP_AFTER_FRAME is not None:
        image_paths = image_paths[0:STOP_AFTER_FRAME]
    tqdm_iter = tqdm(image_paths, desc="- "+f"{subfolder:<8}", unit=" images")
    for i, filename in enumerate(tqdm_iter):
        if not has_read_first:
            img = cv2.imread(filename)
            height, width, layers = img.shape
            original_size = (width, height)
            has_read_first = True
        img_array.append(os.path.join(
            BASE_FOLDER, RECORDING_FOLDER, subfolder, filename))

    folder_dict[subfolder] = img_array

if SAVE_VIDEO_TUBES and len(folder_dict['_img']) < MIN_TUBE_LENGTH:
    warnings.warn(("Skipping SAVE_VIDEO_TUBES functions because video length ("
                   + str(len(folder_dict['_img'])) +
                   ") is shorter than MIN_TUBE_LENGTH ("
                   + str(MIN_TUBE_LENGTH)+")"), RuntimeWarning)
    SAVE_VIDEO_TUBES = False

#
# Generate and write x-in-1 Output Video, also calculate bboxe tubes if needed
#
print("Writing video file...")
if len(OUTPUT_VIDEO_MODES) == 3:
    OUTPUT_VIDEO_MODES.append('black')

size = original_size
if len(OUTPUT_VIDEO_MODES) == 2:
    size = (2*size[0], size[1])  # double width
elif len(OUTPUT_VIDEO_MODES) == 4:
    size = (2*size[0], 2*size[1])  # double width and height
elif len(OUTPUT_VIDEO_MODES) > 4:
    raise Exception("there currently is a maximum of 4 splitscreen videos")

# generates a mode name using the first two characters of each output video
mode_str = ''.join([of[:2] for of in OUTPUT_VIDEO_MODES])
out = cv2.VideoWriter(os.path.join(BASE_FOLDER, RECORDING_FOLDER, 'output_'+mode_str+'.mp4'), cv2.VideoWriter_fourcc(*'mp4v'), FRAMERATE,
                      size) if USE_LOSSY else cv2.VideoWriter(os.path.join(BASE_FOLDER, RECORDING_FOLDER, subfolder, 'output_'+mode_str+'.avi'),
                                                              cv2.VideoWriter_fourcc(*'png '), FRAMERATE, size)

IDB = InstanceDB()
frameNr = 0
tubeslist = []
for img_path in tqdm(folder_dict['_img'], desc="- "+f"{mode_str:<8}", unit=" images"):
    mode_images = {}

    mode_images['original'] = cv2.imread(img_path)
    mode_images['mask'] = cv2.imread(folder_dict['_layer'][frameNr])

    if 'overlay' in OUTPUT_VIDEO_MODES:
        OVERLAY_ALPHA = 0.5
        mode_images['overlay'] = cv2.addWeighted(
            mode_images['original'], OVERLAY_ALPHA, mode_images['mask'], 1-OVERLAY_ALPHA, 0.0)

    if 'black' in OUTPUT_VIDEO_MODES:
        mode_images['black'] = np.zeros_like(mode_images['original'])

    if 'oneclass' in OUTPUT_VIDEO_MODES:
        col = name2color[ONECLASS_CLASSNAME]
        bwmask = (np.all(mode_images['mask'] ==
                         col, axis=2)*255).astype('uint8')
        mode_images['oneclass'] = cv2.cvtColor(bwmask, cv2.COLOR_GRAY2RGB)

    if 'bbox' in OUTPUT_VIDEO_MODES:
        for label in name2color.keys():
            if label not in NO_ACTION_LABELS:
                col = name2color[label]
                bwmask = (np.all(mode_images['mask'] == col, axis=2)
                          * 255).astype('uint8')
                # print("bwmask for label",label,"and color",col,"has",np.count_nonzero(bwmask),"true pixels")

                # find the contours in the thresholded image, then sort the contours by their area
                cnts = cv2.findContours(bwmask.copy(), cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)
                cnts = imutils.grab_contours(cnts)
                cnts_sorted = sorted(cnts, key=cv2.contourArea, reverse=True)
                # filter out all contours that are smaller than a (square) percent of the original image
                cnts_sorted = [c for c in cnts_sorted if cv2.contourArea(c) > (
                    bwmask.shape[0]*bwmask.shape[1]/(100*100))]
                # print("found "+str(len(css))+" contours for "+label)
                for c in cnts_sorted:
                    # Extract segmantation mask and bboxes for just this instance / contour
                    x, y, w, h = cv2.boundingRect(c)
                    inst_segm_bbox = np.array(
                        [[x, y], [x, y+h], [x+w, y+h], [x+w, y]])
                    inst_segm_rbox = np.int0(cv2.boxPoints(cv2.minAreaRect(c)))
                    inst_segm_mask = cv2.drawContours(
                        np.zeros_like(bwmask), [c], 0, (255, 255, 255), -1)
                    # TODO: Group very close contours to one?
                    # find closest match from previous frame to keep instance id:

                    #print("getting instancesInPrevFrame", label, frameNr-1, IDB)
                    instancesInPrevFrame = IDB.get_instances_of_type_in_frame(
                        label, frameNr-1)
                    # print("instancesInPrevFrame:",instancesInPrevFrame)
                    if len(instancesInPrevFrame) > 0:
                        # 2) compare with previous frames versions of (1) using IOU
                        IOUs = [(prev_inst.instance_id, hf.get_equal_white_pixel_count(prev_inst.get_frame_with_nr(frameNr-1).segm_mask, inst_segm_mask))
                                for prev_inst in instancesInPrevFrame]
                        # 3) select instanceid with most TRUEs in comparison / create new instanceid if no TRUEs found.
                        best_previd, best_iou = sorted(
                            IOUs, key=lambda x: x[1], reverse=True)[0]
                        # if at least 1 mask pixel is equal and instanceid is not yet used in current frame
                        # TODO: is choosing second best previous instead of new number better?
                        # TODO: more robust tracking to get less, but longer tube videos
                        curInstancesInFrame = IDB.get_instance_ids_in_frame(
                            frameNr)
                        if best_iou > 0 and best_previd not in curInstancesInFrame:
                            instanceid = best_previd
                        else:
                            instanceid = IDB.get_unused_instance_id()

                    else:
                        instanceid = IDB.get_unused_instance_id()
                    #print("appending frame "+str(frameNr)+" to instanceid="+str(instanceid))
                    IDB.append_frame_to_instance(
                        instanceid, InstanceFrameData(frameNr, inst_segm_mask, inst_segm_bbox, inst_segm_rbox), label)
                    # print(IDB)

        image = mode_images['original'].copy()
        # loop through all instances that occur in the current frames
        for instance in IDB.get_instances_in_frame(frameNr):
            # get bbox of that instance in the current frame:
            bbox = instance.get_frame_with_nr(frameNr).segm_bbox
            label_color = name2color[instance.instance_of]
            cv2.drawContours(image, [bbox], -1, label_color, 3)
            cv2.putText(image, instance.instance_of + " " + str(instance.instance_id),
                        tuple(bbox[0]), cv2.FONT_HERSHEY_SIMPLEX, 1, label_color, 2, cv2.LINE_AA)

        #cv2.imshow("Image", image)
        # cv2.waitKey(0)
        mode_images['bbox'] = image

    if len(mode_images) == 1:
        output_img = list(mode_images)[0]
    elif len(mode_images) == 2:
        output_img = np.concatenate(mode_images, axis=1)
    elif len(mode_images) == 4:
        output_img = np.concatenate((np.concatenate((mode_images[OUTPUT_VIDEO_MODES[0]], mode_images[OUTPUT_VIDEO_MODES[1]]), axis=1),
                                     np.concatenate((mode_images[OUTPUT_VIDEO_MODES[2]], mode_images[OUTPUT_VIDEO_MODES[3]]), axis=1)), axis=0)
    else:
        raise Exception("Invalid Combination of Image modes:",
                        list(mode_images.keys()))

    out.write(output_img)
    deletedInstances = IDB.clean(frameNr)
    if SAVE_VIDEO_TUBES:
        tubeslist.extend([Tube(i) for i in deletedInstances])
    frameNr += 1

deletedInstances = IDB.clean(frameNr)
if SAVE_VIDEO_TUBES:
    tubeslist.extend([Tube(i) for i in deletedInstances])

out.release()

#
# Save videos of the generated bbox tubes if needed
#
if SAVE_VIDEO_TUBES:
    print("Writing mini-video tubes...")
    tubeslist = [tube for tube in tubeslist
                 if tube.max_frame - tube.min_frame >= MIN_TUBE_LENGTH]

    print(tubeslist)

    tube_folder = os.path.join(
        BASE_FOLDER, RECORDING_FOLDER, VIDEO_TUBES_FOLDER)

    for tube in tqdm(tubeslist, desc="- tubes   ", unit=" tubes"):
        labelfolder = os.path.join(
            BASE_FOLDER, RECORDING_FOLDER, VIDEO_TUBES_FOLDER, tube.label)
        if not os.path.exists(labelfolder):
            os.makedirs(labelfolder)

        mw = original_size[0]
        mh = original_size[1]
        crop_min_x = tube.min_x - TUBE_PADDING if tube.min_x - TUBE_PADDING > 0 else 0
        crop_min_y = tube.min_y - TUBE_PADDING if tube.min_y - TUBE_PADDING > 0 else 0
        crop_max_x = tube.max_x + TUBE_PADDING if tube.max_x + TUBE_PADDING < mw else mw
        crop_max_y = tube.max_y + TUBE_PADDING if tube.max_y + TUBE_PADDING < mh else mh

        size = (crop_max_x-crop_min_x, crop_max_y-crop_min_y)
        out = cv2.VideoWriter(os.path.join(labelfolder, RECORDING_FOLDER+'_tube_'+str(tube.tube_id)+'.mp4'), cv2.VideoWriter_fourcc(*'mp4v'), FRAMERATE,
                              size) if USE_LOSSY else cv2.VideoWriter(os.path.join(labelfolder, RECORDING_FOLDER+'_tube_'+str(tube.tube_id)+'.avi'),
                                                                      cv2.VideoWriter_fourcc(*'png '), FRAMERATE, size)

        for frame_nr in range(tube.min_frame, tube.max_frame+1):
            full_img = cv2.imread(folder_dict['_img'][frame_nr])
            cropped_img = full_img[crop_min_y:crop_max_y,
                                   crop_min_x:crop_max_x]
            out.write(cropped_img)

        out.release()


print('\033[92m'+"Done!"+'\033[0m')
