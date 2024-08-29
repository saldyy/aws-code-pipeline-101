from constructs import Construct

from aws_cdk import (
    CfnOutput,
    RemovalPolicy,
    Stack,
    aws_ecr,
    aws_iam as iam
) 

class EcrStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        repository = aws_ecr.Repository(
                self,
                id="GolangRepository",
                repository_name="golang-repository",
                image_scan_on_push=False,
                removal_policy=RemovalPolicy.DESTROY
                )

        ecr_access_role = iam.Role(
                self,
                "EcrAccessRole",
                assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
                role_name="ecr-access-role"
                )

        repository.grant_pull_push(ecr_access_role)

        CfnOutput(self, id="RepositoryArn", value=repository.repository_arn)
        CfnOutput(self, id="IamAccessRoleArn", value=ecr_access_role.role_arn)

        self.repository_arn = repository.repository_arn
        self.iam_access_role = ecr_access_role

