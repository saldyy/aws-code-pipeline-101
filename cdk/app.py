#!/usr/bin/env python3

import aws_cdk as cdk

from cdk.codestar_connection import PipelineStack


app = cdk.App()
PipelineStack(app, "PipelineStack-golang-cicd")

app.synth()
