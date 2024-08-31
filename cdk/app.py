#!/usr/bin/env python3

import aws_cdk as cdk

from cdk import codestar_connection
from cdk.code_pipeline import PipelineStack
from cdk.vpc import VpcStack

app = cdk.App()
codestar_connection = "arn:aws:codeconnections:ap-southeast-1:454159633175:connection/686db3a7-1624-424f-8b7f-76abfe10fc3f"

vpc_stack = VpcStack(app, "Vpc-golang-cicd")
PipelineStack(app,
              "Pipeline-golang-cicd",
              connection_arn=codestar_connection,
              )

app.synth()
