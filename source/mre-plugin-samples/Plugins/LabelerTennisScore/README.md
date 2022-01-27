# LabelerTennisScore #

**MRE Plugin Class**
- Labeler 

**Description**:

This plugin extract score from the scorebox detection output.

**Use Cases**:
- Game point/Set point/Match point detection

**Dependencies**:
- MRE Helper libraries
- Scipy
- OpenCV

**ML Model dependencies**:

**Other plugin dependencies**:
- DetectScoreBox

**Parameter inputs**:


**Output attributes**:
- BreakPoint >>  Boolean value for breakpoint
- GamePoint >>  Boolean value for gamepoint
- SetPoint >>  Boolean value for setpoint
- MatchPoint >> Boolean value for matchpoint

**IAM permissions (least privilege)**:
- S3
