# LabelerExample #

**MRE Plugin Class**
- Labeler

**Description**:

This plugin sample is a simple example of how to construct a label for a segment. Labels can be any string that helps identify a segment/clip amongst all the others for an event. It's essentially a formatter of featurer detector data.


**Use Cases**:
- Any segment that can benefit from refinement of the in/out placement.

**Dependencies**:
- MRE Helper libraries

**ML Model dependencies**:
- None

**Other plugin dependencies**:
- TBD

A label for a segment could be done with just the start and end time if you want and require no dependent data. If your desired label is comprised of data detected by other featurer plugins, then include them as dependencies. For example, if you wanted to label a segment with a score, then whatever plugins gather that data, should be listed as dependent.

**Parameter inputs**:
- None

**Output attributes**:
- None

**IAM permissions (least privilege)**:
- None
