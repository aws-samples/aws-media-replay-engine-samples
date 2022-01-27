# LabelerTennisAceDoubleFault #

**MRE Plugin Class**
- Labeler  

**Description**:

This plugin classifies a segment to be ace serve, double fault, or regular rally play 

**Use Cases**:
- Ace/Double Fault detection  

**Dependencies**:
- MRE Helper libraries  
- Scipy  
- OpenCV  

**ML Model dependencies**:
- AudioEmbeddingModel  
- AudioEmbeddingClassificationModel  

**Other plugin dependencies**:

**Parameter inputs**:


**Output attributes**:
- Label >> Name of the feature be detected in this plugin  
- Ace >>  Boolean value for ace serve  
- DoubleFault >>  Boolean value for double fault serve  

**IAM permissions (least privilege)**:
- S3
