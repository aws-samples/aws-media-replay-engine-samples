# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import os
import boto3
from botocore.exceptions import ClientError
import math
import time
import cv2

from MediaReplayEnginePluginHelper import OutputHelper
from MediaReplayEnginePluginHelper import PluginHelper
from MediaReplayEnginePluginHelper import Status
from MediaReplayEnginePluginHelper import DataPlane

rek_client = boto3.client('rekognition')

def consolidate_rek_results(mre_pluginhelper, rek_faces):
    results = []

    for face in rek_faces:
        result = {}

        result['Start'] = mre_pluginhelper.get_segment_absolute_time(0)
        result['End'] = mre_pluginhelper.get_segment_absolute_time(0)
        result['Label'] = comprehend_results['Sentiment']
        result['primary_sentiment'] = result['Label']

        results.append(result)

    return results

def lambda_handler(event, context):

    print(event)

    results = []
    mre_dataplane = DataPlane(event)

    # 'event' is the input event payload passed to Lambda
    mre_outputhelper = OutputHelper(event)
    mre_pluginhelper = PluginHelper(event)

    try :

        # Download the HLS video segment from S3
        media_path = mre_dataplane.download_media()

        _, chunk_filename = head, tail = os.path.split(event['Input']['Media']["S3Key"])

        # Frame rate for sampling
        p_fps = int(event["Profile"]["ProcessingFrameRate"]) #i.e. 5
        v_fps = int(event["Input"]["Metadata"]["HLSSegment"]["FrameRate"]) #i.e. 25
        frameRate = int(v_fps/p_fps)

        cap = cv2.VideoCapture(media_path)

        # get plugin config values
        faces_collection_id = event['Plugin']['Configuration']['faces_collection_id']
        max_faces = event['Plugin']['Configuration']['max_faces']
        quality_filter = event['Plugin']['Configuration']['quality_filter']
        minimum_confidence = event['Plugin']['Configuration']['min_confidence']

        while(cap.isOpened()):
            frameId = cap.get(1) #current frame number
            ret, frame = cap.read()

            if (ret != True):
                break

            # skip frames to meet processing FPS requirement
            if (frameId % math.floor(frameRate) == 0):
                hasFrame, imageBytes = cv2.imencode(".jpg", frame)
                if(hasFrame):

                    #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition.html#Rekognition.Client.index_faces
                    #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition.html#Rekognition.Client.search_faces_by_image
                    response = rek_client.search_faces_by_image(
                        CollectionId = faces_collection_id,
                        Image = {'Bytes': imageBytes.tobytes(),},
                        QualityFilter = quality_filter,
                        MaxFaces = max_faces,
                        FaceMatchThreshold = minimum_confidence
                    )

                    print(response)

            #process results
            #results = consolidate_rek_results(mre_pluginhelper, response)
             
            print(results)

        # Add the results of the plugin to the payload (required if the plugin status is "complete"; Optional if the plugin has any errors)
        mre_outputhelper.add_results_to_output(results)

        # Persist plugin results for later use
        mre_dataplane.save_plugin_results(results)

        # Update the processing status of the plugin (required)
        mre_outputhelper.update_plugin_status(Status.PLUGIN_COMPLETE)

        # Returns expected payload built by MRE helper library
        return mre_outputhelper.get_output_object()

    except Exception as e:
        print(e)

        # Update the processing status of the plugin (required)
        mre_outputhelper.update_plugin_status(Status.PLUGIN_ERROR)

        # Re-raise the exception to MRE processing where it will be handled
        raise
