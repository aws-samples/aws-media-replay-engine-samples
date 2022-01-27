# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import sys

from aws_cdk import (
    core as cdk,
    aws_iam as iam
)
from chalice.cdk import Chalice

# Ask the Python interpreter to search for modules in the parent folder. This is required to access the harvester_config.py.
sys.path.append(os.path.join(
    os.path.dirname(os.path.dirname(__file__)), '../'))

import harvester_config


RUNTIME_SOURCE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), os.pardir, 'runtime')


class ChaliceApp(cdk.Stack):

    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)
        
        # EC2 IAM Role
        self.ec2_role = iam.Role(
            self,
            "MRESamplesHLSHarvesterEC2Role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com")
        )

        # EC2 IAM Role - API GW Invoke Permissions
        self.ec2_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "execute-api:Invoke",
                    "execute-api:ManageConnections"
                ],
                resources=[f"arn:aws:execute-api:{cdk.Stack.of(self).region}:{cdk.Stack.of(self).account}:*"]
            )
        )

        # EC2 IAM Role - SSM Permissions
        self.ec2_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ssm:DescribeParameters",
                    "ssm:GetParameter*"
                ],
                resources=[f"arn:aws:ssm:{cdk.Stack.of(self).region}:{cdk.Stack.of(self).account}:parameter/MRE*"]
            )
        )

        # EC2 IAM Role - SQS Permissions
        self.ec2_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "sqs:DeleteMessage",
                    "sqs:ReceiveMessage"
                ],
                resources=[f"arn:aws:sqs:{cdk.Stack.of(self).region}:{cdk.Stack.of(self).account}:{harvester_config.SQS_QUEUE_URL.split('/')[-1]}"]
            )
        )

        # EC2 IAM Role - S3 Permissions
        self.ec2_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:Put*"
                ],
                resources=[f"arn:aws:s3:::{harvester_config.DESTINATION_S3_BUCKET}"]
            )
        )

        # Chalice IAM Role
        self.chalice_role = iam.Role(
            self,
            "MRESamplesHLSHarvesterChaliceRole",
            assumed_by=iam.ServicePrincipal(service="lambda.amazonaws.com"),
            description="Role used by the MRE Samples HLS Harvester Chalice Lambda function"
        )

        # Chalice IAM Role - PassRole Permission
        self.chalice_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "iam:PassRole"
                ],
                resources=[self.ec2_role.role_arn]
            )
        )

        # Chalice IAM Role - EC2 Permissions
        self.chalice_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ec2:Describe*",
                    "ec2:GetConsole*"
                ],
                resources=["*"]
            )
        )

        self.chalice_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ec2:RunInstances"
                ],
                resources=[
                    "arn:aws:ec2:*:*:subnet/subnet-subnet-id",
                    "arn:aws:ec2:*:*:network-interface/*",
                    "arn:aws:ec2:*:*:instance/*",
                    "arn:aws:ec2:*:*:volume/*",
                    "arn:aws:ec2:*::image/ami-*",
                    "arn:aws:ec2:*:*:key-pair/*",
                    "arn:aws:ec2:*:*:security-group/*"
                ]
            )
        )

        self.chalice = Chalice(
            self, "ChaliceApp", source_dir=RUNTIME_SOURCE_DIR,
            stage_config={
                "environment_variables": {
                    "EC2_INSTANCE_TYPE": harvester_config.EC2_INSTANCE_TYPE,
                    "SUBNET_ID": harvester_config.SUBNET_ID,
                    "SECURITY_GROUPS_IDS": harvester_config.SECURITY_GROUPS_IDS,
                    "EC2_IAM_INSTANCE_PROFILE_ROLE_NAME": self.ec2_role.role_name,
                    "MRE_REGION" : harvester_config.MRE_REGION,
                    "SQS_QUEUE_URL" : harvester_config.SQS_QUEUE_URL,
                    "SQS_WAIT_TIME_SECS": str(harvester_config.SQS_WAIT_TIME_SECS),
                    "API_KEY": harvester_config.API_KEY,
                    "CHUNK_SIZE": str(harvester_config.CHUNK_SIZE),
                    "DESTINATION_S3_BUCKET": harvester_config.DESTINATION_S3_BUCKET
                },
                "tags": {
                    "Project": "MRE Samples",
                    "Application": "HLS Harvester"
                },
                "manage_iam_role": False,
                "iam_role_arn": self.chalice_role.role_arn,
                "lambda_functions": {
                    "provision_ec2_process_events": {
                        "lambda_timeout": 600
                    }
                }
            }
        )
