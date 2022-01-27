# DetectSceneChange #

**MRE Plugin Class**
- Featurer

**Description**:

This plugin uses FFMPEG to determine where scene changes are occurring in video. This can be used for optimizing in/out placements.


**Use Cases**:
- Any segment that can benefit from refinement of the in/out placement.

**Dependencies**:
- MRE Helper libraries
- FFMPEG >> setup as a Lambda Layer

**ML Model dependencies**:
- None

**Other plugin dependencies**:
- None

**Parameter inputs**:
- scene_threshold >> Range of sane value is between 0.3 and 0.5 per the FFMPEG docs. This value affects the threshold for change detection.

**Output attributes**:
- None

**IAM permissions (least privilege)**:
- S3
