# DetectAudioScene #

**MRE Plugin Class**
- Featurer

**Description**:

This plugin detects different audio scenes in tennis match

**Use Cases**:
- Detect crowd noise/commentator talk/ball hitting/quite scence in tennis match
- Detect any audio distinguishable scenarios in the video

**Dependencies**:
- MRE Helper libraries  
- FFMPEG  
- audio2numpy
- Scipy  
- OpenCV  

**ML Model dependencies**:
- AudioSpetrumClassificationModel

**Other plugin dependencies**:

**Parameter inputs**:
- minimum_confidence >> minimum confidence for classification
- TimeWindowLength >> time window length
- LowCut  >> low cut freq
- HighCut >> high cut freq

**Output attributes**:
- Label >> Name of the feature be detected in this plugin
- AudioScene >> Name of the audio scene

**IAM permissions (least privilege)**:
- S3
