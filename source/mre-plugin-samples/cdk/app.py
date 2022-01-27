# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

#!/usr/bin/env python3

from aws_cdk import core as cdk
from stacks.mre_plugins_stack import MrePluginsStack

app = cdk.App()
MrePluginsStack(app, "aws-mre-plugin-samples")

app.synth()
