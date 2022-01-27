# Detect Speech #

**MRE Plugin Class**
- Featurer

**Description**:

When optimizing in/out placement for segments/clips it's sometimes desirable to avoid interruption of the announcer. This plugin processes audio tracks to detect pauses in speech that may offer better location of in/out placement. It can be used with the general purposes MRE optimization plugin.

**Applies to Media Type**:
- Audio

**Use Cases**:
- Can be used to generate data that gets used by an optimizer plugin to adjust the in/out times of a segment to avoid interrupting an announcer
- Could be enhanced/modified to detect specific words or phrases that could be leveraged in replay highlight priorities (weightings).

**Dependencies**:
- MRE Helper libraries
- ffmpeg >> suggest a custom Lambda Layer
- Amazon Transcribe
- Boto3

**ML Model dependencies**:
- none

**Other plugin dependencies**:
- none

**Parameter inputs**:
- silence_duration_sec
- input_bucket_name >> just the bucket name itself: my-bucket. This is an intermediate storage location for the extracted audio file.
- output_bucket_name >> this is needed to have the Transcribe service write results out to

**Output attributes**:
- Label >> the value 'speech present' will appear when detected by the presence of a 'pronunciation' type result in the transcription
- Transcription >> raw Transcribe results

**IAM permissions (least privilege)**:
- Transcribe - StartTranscriptionJob
- Transcribe - GetTranscriptionJob
- S3 - PutObject on intermediate bucket with extracted audio file
- S3 - GetObject on Transcribe output bucket AND input_bucket_name specified in parameters
- S3 - ListBucket on Transcribe output bucket AND input_bucket_name specified in parameters

**Post-Install Required Actions**:
- Review the parameter input values and set accordingly (S3 bucket and region) as the default is not valid
- Update the IAM Policy to reflect the S3 bucket permissions needed
- Adjust the lambda function timeout setting to accommodate the size (length) of the chunk. Larger chunks have more audio to transcribe which takes longer to process.
