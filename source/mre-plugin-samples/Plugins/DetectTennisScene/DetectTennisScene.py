# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import os
import boto3
import cv2
import math
from MediaReplayEnginePluginHelper import OutputHelper
from MediaReplayEnginePluginHelper import Status
from MediaReplayEnginePluginHelper import DataPlane

rek_client=boto3.client('rekognition')

def lambda_handler(event, context):

    print(event)

    results = []
    mre_dataplane = DataPlane(event)

    # 'event' is the input event payload passed to Lambda
    mre_outputhelper = OutputHelper(event)

    try:

        # Download the HLS video segment from S3
        media_path = mre_dataplane.download_media()

        # plugin params
        _, chunk_filename = head, tail = os.path.split(event['Input']['Media']["S3Key"])
        model_endpoint = str(event['Plugin']['ModelEndpoint'])
        minimum_confidence = int(event["Plugin"]["Configuration"]["minimum_confidence"]) #30

        # Frame rate for sampling
        p_fps = int(event["Profile"]["ProcessingFrameRate"]) #i.e. 5
        v_fps = int(event["Input"]["Metadata"]["HLSSegment"]["FrameRate"]) #i.e. 25
        frameRate = int(v_fps/p_fps)

        cap = cv2.VideoCapture(media_path)

        while(cap.isOpened()):
            frameId = cap.get(1) #current frame number
            ret, frame = cap.read()

            if (ret != True):
                break

            # skip frames to meet processing FPS requirement
            if (frameId % math.floor(frameRate) == 0):
                hasFrame, imageBytes = cv2.imencode(".jpg", frame)
                if(hasFrame):
                    #Call DetectCustomLabels
                    #print(f'working on frame {frameId}')
                    response = rek_client.detect_custom_labels(
                        Image={'Bytes': imageBytes.tobytes(),},
                        MinConfidence = minimum_confidence,
                        ProjectVersionArn = model_endpoint
                    )

                    elabel = {}
                    if len(response['CustomLabels']) > 0:
                        elabel['Label'] = response["CustomLabels"][0]['Name']
                        elabel["Confidence"] = '{:.2f}'.format(response["CustomLabels"][0]["Confidence"])

                        # Get timecode from frame
                        elabel["Start"] = mre_dataplane.get_frame_timecode(frameId)
                        elabel["End"] = elabel["Start"]
                        elabel["frameId"] = frameId
                        results.append(elabel)

                    else:
                        frameId = int(frameId)
                        results.append({'Label': 'NA', 'Confidence': '-1', 'Start': frameId, 'End': frameId, 'frameId': frameId })

        print(f'results:{results}')

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
