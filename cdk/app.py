#!/usr/bin/env python3

import aws_cdk as cdk

from cdk import codestar_connection
from cdk.codestar_connection import GithubConnection
from cdk.code_pipeline import PipelineStack
from cdk.ecr import EcrStack

app = cdk.App()
codestar_connection = "arn:aws:codeconnections:ap-southeast-1:454159633175:connection/686db3a7-1624-424f-8b7f-76abfe10fc3f"
ecr_stack = EcrStack(app, "GolangEcr")
PipelineStack(app,
              "Pipeline-golang-cicd",
              connection_arn=codestar_connection,
              ecr_arn=ecr_stack.repository_arn,
              ecr_iam_access_role_arn=ecr_stack.iam_access_role
              )

app.synth()
