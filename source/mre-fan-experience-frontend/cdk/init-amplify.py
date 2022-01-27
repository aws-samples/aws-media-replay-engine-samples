# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import json
import sys


def main(region, profile=None):
    cdk_outputs = open('cdk-outputs.json', 'r')
    cdk_outputs_json = json.loads(cdk_outputs.read())

    amplify_app_id = cdk_outputs_json['mre-fan-experience-frontend-stack']['webAppId']
    user_pool_id = cdk_outputs_json['mre-fan-experience-frontend-stack']['userPoolId']
    identity_pool_id = cdk_outputs_json['mre-fan-experience-frontend-stack']['identityPoolId']
    app_client_id = cdk_outputs_json['mre-fan-experience-frontend-stack']['appClientId']

    if profile:
        boto3.setup_default_session(profile_name=profile)

    ssm_client = boto3.client('ssm', region_name=region)

    control_plain_endpoint = ssm_client.get_parameter(
        Name='/MRE/ControlPlane/EndpointURL',
        WithDecryption=False
    )

    data_plane_endpoint = ssm_client.get_parameter(
        Name='/MRE/DataPlane/EndpointURL',
        WithDecryption=False
    )

    amplify_client = boto3.client('amplify', region_name=region)

    amplify_client.update_app(
        appId=amplify_app_id,
        customHeaders=f'''
        customHeaders:
          - pattern: '**/*'
            headers:
              - key: 'Strict-Transport-Security'
                value: 'max-age=31536000; includeSubDomains'
              - key: 'X-Frame-Options'
                value: 'SAMEORIGIN'
              - key: 'X-XSS-Protection'
                value: '1; mode=block'
              - key: 'X-Content-Type-Options'
                value: 'nosniff'
              - key: 'Content-Security-Policy'
                value: >-
                    default-src 'self' https://cognito-identity.{region}.amazonaws.com
                    *.execute-api.{region}.amazonaws.com https://*.s3.amazonaws.com; style-src 'self'
                    'unsafe-inline'; connect-src 'self'
                    https://cognito-idp.{region}.amazonaws.com/
                    https://cognito-identity.{region}.amazonaws.com
                    *.execute-api.{region}.amazonaws.com; script-src 'self'
                    'unsafe-inline' https://cognito-idp.{region}.amazonaws.com/
                    https://cognito-identity.{region}.amazonaws.com
                    *.execute-api.{region}.amazonaws.com; img-src 'self' https://*.s3.amazonaws.com;
                    media-src 'self' https://*.s3.amazonaws.com;
            ''',
        environmentVariables={
            "REACT_APP_BASE_API": control_plain_endpoint['Parameter']["Value"],
            "REACT_APP_DATA_PLANE_API": data_plane_endpoint['Parameter']["Value"],
            "REACT_APP_REGION": region,
            "REACT_APP_USER_POOL_ID": user_pool_id,
            "REACT_APP_APP_CLIENT_ID": app_client_id,
            "REACT_APP_IDENTITY_POOL_ID": identity_pool_id,
            "REACT_APP_CLOUDFRONT_PREFIX": "replace_with_url"
        },
        customRules=[
            {
                'source': '</^((?!\.(css|gif|ico|jpg|js|png|txt|svg|woff|ttf)$).)*$/>',
                'target': '/index.html',
                'status': '200'
            }
        ]
    )

    return 1


if __name__ == "__main__":
    if len(sys.argv) == 3:
        result = main(sys.argv[1], sys.argv[2])
    else:
        result = main(sys.argv[1])

    sys.exit(0) if result else sys.exit(1)
