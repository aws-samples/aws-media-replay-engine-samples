# Detect Faces #

**MRE Plugin Class**
- Featurer

**Description**:

Detect faces from your own collection that you setup in advance. Frames are extracted from the chunk video and analyzed with Amazon Rekognition.

**Applies to Media Type**:
- Video

**Use Cases**:
- Looking for specific players in a segment/clip
- Looking for presenter changes in a keynote to help segmentation
- Looking for movie/tv actors/actresses/news reporters

**Dependencies**:
- MRE Helper libraries
- Boto3
- OpenCV (as a Lambda Layer)

**ML Model dependencies**:
- none

**Other plugin dependencies**:
- Amazon Rekognition face collection (you provide)

**Parameter inputs**:
- faces_collection_id >> Amazon Rekognition ID of the collection to search. This is a custom collection of faces you provide.
- faces_to_find >> An array of face names (ExternalImageId) to find in the frame. These should be a subset of those in the collection.
- max_faces >> Maximum number of faces to return.
- quality_filter >> A filter that specifies a quality bar for how much filtering is done to identify faces (AUTO, NONE, LOW, MEDIUM, or HIGH).
- minimum_confidence >> Specifies the minimum confidence in the face match to return.

**Output attributes**:
- Label >> The number of faces detected that match the names list provided
- Faces_List >> A comma separated list of FaceMatches with the specified ExternalImageId attribute (their name if indexed that way)  
- <a flag indicating the presence of each unique face>

**IAM permissions (least privilege)**:
- Rekognition - SearchFacesByImage

**Post-Install Required Actions**:
- None
