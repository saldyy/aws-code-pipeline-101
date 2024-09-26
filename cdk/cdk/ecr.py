from aws_cdk import (aws_ecr as ecr, Stack)
from constructs import Construct


class EcrStack(Stack):

    def __init__(self, scope: Construct, id, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.repository = ecr.Repository(self, id, repository_name="golang-ci-cd")
