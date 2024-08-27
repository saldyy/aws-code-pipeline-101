#!/usr/bin/env python3

import aws_cdk as cdk

from cdk import codestar_connection
from cdk.codestar_connection import GithubConnection
from cdk.code_pipeline import PipelineStack

app = cdk.App()
codestar_connection = GithubConnection(app, "PipelineStack-golang-cicd")
PipelineStack(app, "Pipeline-golang-cicd", connection_arn=codestar_connection.connection_arn)

app.synth()
