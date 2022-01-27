# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import boto3
from botocore.exceptions import ClientError

from MediaReplayEnginePluginHelper import OutputHelper
from MediaReplayEnginePluginHelper import PluginHelper
from MediaReplayEnginePluginHelper import Status
from MediaReplayEnginePluginHelper import DataPlane


def optimize_segment(segment_mark, segment_type, detectors, config, max_search_window_sec):

    status = None
    opto_segment_mark = segment_mark
    suggested_segment_mark = segment_mark
    offset = 0
    result = {}
    result['Opto' + segment_type] = segment_mark

    print ('Segment starting at: ' + str(segment_mark))
    print(config)

    #loop through all dependent detectors
    for detector in detectors:
        print ('DependentDetector: ' + detector['DependentDetector'])
        print(detector)

        ##### To do, read configuration from dep_plugin_config, which has the bias value, in the lamnda_handler.
        #####  and merge it with segment['DependentDetectorsOutput'], which is the 'detectors' variable here.
        bias = detector['bias'] #'safe range', 'unsafe range'
        print ('Detector bias: ' + bias)

        if segment_type in detector:
            #loop through all the data for the respective detector
            for detection in detector[segment_type]:
                print('Detection starting at ' + str(detection[segment_type]) + ' ending at ' + str(detection['End']))

                if bias == 'safe range':
                    if detection['Start'] <= segment_mark <= detection['End']:
                        # in a good range, but only succeeded if not already failed
                        if not status == False:
                            status = True
                            print('already in safe range')

                    else: # not in a good range
                        status = False
                        #attempt to move it
                        #the offset should start with the point at which the safe range started
                        #the offset should also be within the max search size
                        #the offset should not be less than a previous offset applied in this loop for other detectors
                        print('suggested_segment_mark: ' + str(suggested_segment_mark) + '  segment_mark: ' + str(segment_mark) + '  detection-start: ' + str(detection['Start']) )
                        if segment_type == 'Start':
                            suggested_segment_mark = detection['Start']
                            if abs(suggested_segment_mark - segment_mark) > max_search_window_sec:
                                suggested_segment_mark = segment_mark - max_search_window_sec
                                print('adjusted but limited by max window')
                            else:
                                suggested_segment_mark = detection['Start']
                                print('adjusted to start edge of range')

                        else: #end processing
                            suggested_segment_mark = detection['End']
                            if abs(suggested_segment_mark - segment_mark) > max_search_window_sec:
                                suggested_segment_mark = segment_mark + max_search_window_sec
                                print('adjusted but limited by max window')
                            else:
                                suggested_segment_mark = detection['End']
                                print('adjusted to end edge of range')

                        opto_segment_mark = suggested_segment_mark

                else:
                    if detection['Start'] <= segment_mark <= detection['End']:
                        # in a bad range, but only succeeded if not already failed
                        if not status == False:
                            status = False
                    else: # in a good range
                        status = True

            if len(detector[segment_type]) == 0:
                if bias == 'safe range':
                    #then nothing was in range for a safe optimization
                    status = False
                elif bias == 'safe single marker':
                    status = False
                elif bias == 'unsafe range':
                    if not status:
                        status = True
                elif bias == 'unsafe single marker':
                    if not status:
                        status = True

    result['Opto' + segment_type] = opto_segment_mark

    return result, status


def lambda_handler(event, context):

    print(event)

    mre_dataplane = DataPlane(event)

    # 'event' is the input event payload passed to Lambda
    mre_outputhelper = OutputHelper(event)
    mre_pluginhelper = PluginHelper(event)

    results = []

    try:

        # plugin config
        plugin_config = mre_pluginhelper.get_plugin_configuration()
        print('plugin config:')
        print(plugin_config)

        #this input parameter needs to be configured as part of the MRE plugin registration process
        optimization_search_window_sec = float(plugin_config['optimization_search_window_sec'])

        #Check if this plugin has dependencies and if so, get their respective configuration details
        dep_plugin_config = mre_pluginhelper.get_dependent_plugins_configuration()
        print('dep plugin config: ')
        print(dep_plugin_config)

        #get all pending segments to be optimized and detector data within that time range plus the search window buffer time
        segments = mre_dataplane.get_segment_state_for_optimization(search_window_sec=optimization_search_window_sec)
        print('get_segment_state_for_optimization:')
        print(segments)

        for segment in segments:
            print('Next segment to optimize')
            new_result = {}

            #ignore incomplete segments that only have a start. We know that because the end is set temporarily to that of the start
            if segment['Segment']['Start'] != segment['Segment']['End']:

                #check opto status of the segment and only process those that have not been attempted
                if 'OptoStart' not in segment:
                    segment_type = 'Start'
                    print(segment_type + ' part of segment to optimize')
                    result, status = optimize_segment(segment['Segment'][segment_type], segment_type, segment['DependentDetectorsOutput'], plugin_config, optimization_search_window_sec)
                    print(status)

                    new_result['Start'] = segment['Segment']['Start']
                    if 'End' in segment['Segment']:
                        new_result['End'] = segment['Segment']['End']
                    new_result['OptoStart'] = result['OptoStart']

                    if status:
                        new_result['OptoStartCode'] = 'Opto succeeded'
                    else:
                        new_result['OptoStartCode'] = 'Unsuccessful'


                if 'OptoEnd' not in segment:
                    segment_type = 'End'
                    print(segment_type + ' part of segment to optimize')
                    result, status = optimize_segment(segment['Segment'][segment_type], segment_type, segment['DependentDetectorsOutput'], plugin_config, optimization_search_window_sec)
                    print(status)

                    new_result['Start'] = segment['Segment']['Start']
                    if 'End' in segment['Segment']:
                        new_result['End'] = segment['Segment']['End']
                    new_result['OptoEnd'] = result['OptoEnd']

                    if status:
                        new_result['OptoEndCode'] = 'Opto succeeded'
                    else:
                        new_result['OptoEndCode'] = 'Unsuccessful'

            results.append(new_result)


        # Persist plugin results for later use
        mre_dataplane.save_plugin_results(results)

        # Add the results of the plugin to the payload (required if the plugin status is "complete"; Optional if the plugin has any errors)
        mre_outputhelper.add_results_to_output(results)

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
