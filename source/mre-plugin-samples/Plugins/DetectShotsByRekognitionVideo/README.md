# DetectShotsByRekognitionVideo #

**MRE Plugin Class**
- Featurer

**Description**:

This plugin uses Amazon Rekognition Video API for shot detection. You can check out more details at [this link](https://docs.aws.amazon.com/rekognition/latest/dg/segments.html)

**Use Cases**:
- Any contents where shot detection is needed. Commerical detection is an example.

**Dependencies**:
- MRE Helper libraries
- FFMPEG convert video chunk from ts format to mp4

**ML Model dependencies**:
- None 

**Other plugin dependencies**:
- None

**Parameter inputs**:
- None
 
**Output attributes**:
- Label >> the scene classification tag

**IAM permissions (least privilege)**:
- S3
- APIGatewayInvoke
- SSM
- Rekognition

