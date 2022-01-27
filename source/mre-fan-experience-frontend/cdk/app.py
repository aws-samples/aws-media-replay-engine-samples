# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from aws_cdk import core
from stacks.mre_fan_experience_frontend_stack import MreFanExperienceFrontendStack

app = core.App()

MreFanExperienceFrontendStack(app, "mre-fan-experience-frontend-stack")

app.synth()

