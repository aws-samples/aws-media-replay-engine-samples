# DetectTennisScene #

**MRE Plugin Class**
- Featurer

**Description**:

This plugin uses a tennis scene classification model to determine what the camera scene is. Models that have been tested with it used labels such as:
- near >> camera is close up on a single player
- far >> camera angle is from afar - wide view
- topview >> camera angle is from above
- replay >> event logo present indicating an instant replay is present

**Use Cases**:
- Tennis specific content where the camera angle / scene is needed. Scene classification for segmentation is an example.

**Dependencies**:
- MRE Helper libraries
- OpenCV >> provide as a Lambda Layer

**ML Model dependencies**:
- Requires a ML Model that performs scene classification using Amazon Rekognition Custom Labels

**Other plugin dependencies**:
- None

**Parameter inputs**:
- minimum_confidence >> threshold for confidence in the ML result. 0 would include anything.

**Output attributes**:
- Label >> the scene classification tag
- Confidence >> the inference confidence from the ML endpoint
- frameId >> frame within the video chunk processed. This is for debug.

**IAM permissions (least privilege)**:
- S3
