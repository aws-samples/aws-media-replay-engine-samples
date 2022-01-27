# Pose Classification Model #

**MRE Plugin Class**
- Featurer

**Description**:  
This model takes the output from PoseKeypointDetectionModel, and classify the pose into predefined classes


**Use Cases**:  
- Pointing pose detection in the Soccer demo   
- Serving pose detection in the Tennis demo  
- Any human pose classification  

**Model Type**:  
- Custom Model trained by Amazon SageMaker Autopilot

**Methods for training data collection and annotation**  
- Get output from PoseKeypointsExtractionModel and save as a CSV file
- Add a POSE_CLASS column in the CSV file and annotate each pose with a class name
- An end-to-end solution for pose classification is under development

**Methods for model training**  
- Create an Autopilot job. See details in the Notebook  

**Methods for model hosting**  
- Autopilot job will host an endpoint for the best candiate job
