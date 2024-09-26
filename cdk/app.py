#!/usr/bin/env python3

import aws_cdk as cdk

from cdk import codestar_connection, ecs_cluster
from cdk.code_pipeline import PipelineStack
from cdk.ecr import EcrStack
from cdk.vpc import VpcStack

app = cdk.App()
codestar_connection = "arn:aws:codeconnections:ap-southeast-1:454159633175:connection/686db3a7-1624-424f-8b7f-76abfe10fc3f"

vpc_stack = VpcStack(app, "Vpc-golang-cicd")
ecr_stack = EcrStack(app, "Ecr-golang-cicd")
ecs_cluster_stack = ecs_cluster.EcsStack(app, "Ecs-golang-cicd", vpc=vpc_stack.vpc,
                                         repository=ecr_stack.repository)
PipelineStack(app,
              "Pipeline-golang-cicd",
              connection_arn=codestar_connection,
              task_definition=ecs_cluster_stack.task_definition,
              ecs_service=ecs_cluster_stack.service,
              repository=ecr_stack.repository
)

app.synth()
