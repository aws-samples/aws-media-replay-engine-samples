# DetectAudioSilence #

**MRE Plugin Class**
- Featurer

**Description**:

This plugin uses FFMPEG to determine where silence exists within an audio track. This can be used for optimizing in/out placements.


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
- silence_threshold_db >> Threshold for audio silence in decibels. A value between -30 and -60 would be reasonable.
- silence_duration_sec >> Number of seconds that the audio level must be sustained in order to be detected.

**Output attributes**:
- None

**IAM permissions (least privilege)**:
- S3
