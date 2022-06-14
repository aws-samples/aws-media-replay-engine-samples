# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import os
from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    CfnParameter,
    CfnOutput,
    aws_iam as iam,
    aws_lambda as _lambda,
)


class MrePluginsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.helper_layer_arn = CfnParameter(
            self,
            "helperlayerarn",
            type="String"
        )

        # Import the MediaReplayEnginePluginHelper layer
        self.plugin_helper_layer = _lambda.LayerVersion.from_layer_version_arn(
            self,
            "MediaReplayEnginePluginHelperLayer",
            layer_version_arn=self.helper_layer_arn.value_as_string
        )

        plugins = [name for name in os.listdir('../Plugins') if os.path.isdir(os.path.join('../Plugins', name))]

        for plugin_name in plugins:
            with open(f'../Plugins/{plugin_name}/config.json') as f:
                plugin_config = json.load(f)

                # IAM Role for the Plugin
                self.lambda_role = iam.Role(
                    self,
                    f"{plugin_name}Role",
                    assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
                )

                ### START: MRE IAM Policies for the Plugin ###
                self.lambda_role.add_to_policy(
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=[
                            "logs:CreateLogGroup",
                            "logs:CreateLogStream",
                            "logs:PutLogEvents"
                        ],
                        resources=[f"arn:aws:logs:{Stack.of(self).region}:{Stack.of(self).account}:log-group:/aws/lambda/{plugin_name}:*"]
                    )
                )

                self.lambda_role.add_to_policy(
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=[
                            "ssm:DescribeParameters",
                            "ssm:GetParameter*"
                        ],
                        resources=[f"arn:aws:ssm:{Stack.of(self).region}:{Stack.of(self).account}:parameter/MRE*"]
                    )
                )

                self.lambda_role.add_to_policy(
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=[
                            "execute-api:Invoke",
                            "execute-api:ManageConnections"
                        ],
                        resources=[f"arn:aws:execute-api:{Stack.of(self).region}:{Stack.of(self).account}:*"]
                    )
                )
                ### END: MRE IAM Policies for the Plugin ###

                # Custom IAM Policies for the Plugin
                if "IAMPolicyDocument" in plugin_config["Lambda"]:
                    for policy in plugin_config["Lambda"]["IAMPolicyDocument"]:
                        self.lambda_role.add_to_policy(
                            iam.PolicyStatement(
                                effect=iam.Effect.ALLOW,
                                actions=policy["Actions"],
                                resources=[resource.replace("region", Stack.of(self).region).replace("account-id", Stack.of(self).account) for resource in policy["Resources"]]
                            )
                        )

                self.plugin_name = _lambda.Function(
                    self,
                    f"{plugin_name}Lambda",
                    description=plugin_config["MRE"]["Plugin"]["Description"],
                    function_name=plugin_name,
                    runtime=_lambda.Runtime.PYTHON_3_8,
                    code=_lambda.Code.from_asset(f'../Plugins/{plugin_name}'),
                    handler=plugin_config["Lambda"]["Handler"],
                    role=self.lambda_role,
                    memory_size=plugin_config["Lambda"]["MemorySize"],
                    timeout=Duration.seconds(plugin_config["Lambda"]["TimeoutSecs"]),
                    layers=[
                        self.plugin_helper_layer
                    ]
                )

                # Add the Plugin Lambda ARN to CFN Output
                CfnOutput(
                    self,
                    plugin_name,
                    export_name=plugin_name,
                    value=self.plugin_name.latest_version.function_arn
                )
