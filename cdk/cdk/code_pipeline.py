from aws_cdk.aws_iam import IRole
from constructs import Construct

from aws_cdk import (
    Stack,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,

) 

class PipelineStack(Stack):

    def __init__(self, scope: Construct, id: str, connection_arn: str, ecr_arn: str,
                 ecr_iam_access_role_arn = IRole, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        pipeline = codepipeline.Pipeline(self, "Pipeline")

        source_output = codepipeline.Artifact(artifact_name="SourceArtifact")
        source_action = codepipeline_actions.CodeStarConnectionsSourceAction(
            action_name="Source",
            connection_arn=connection_arn,
            owner="saldyy",
            repo="aws-code-pipeline-101",
            output=source_output
        )
        pipeline.add_stage(stage_name="Source", actions=[source_action])


        test_project = codebuild.PipelineProject(
            self, "GolangTestProject",
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "runtime-versions": {
                            "golang": "1.21.4"
                        }
                    },
                    "build": {
                        "commands": [
                            "echo --------START--------",
                            "go version",
                            "cd app",
                            "make test"
                        ]
                    }
                }
            }),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0
            )
        )
        test_action = codepipeline_actions.CodeBuildAction(
            action_name="RunTests",
            project=test_project,
            input=source_output
        )
        pipeline.add_stage(stage_name="Test", actions=[test_action])


        build_project = codebuild.PipelineProject(
            self, "GolangBuildProject",
            role=ecr_iam_access_role_arn,
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "build": {
                        "commands": [
                            "echo --------START BUILD--------",
                            "cd app",
                            "aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin {ecr_arn}".format(ecr_arn=ecr_arn),
                            "docker build -t golang-proj-$CODEBUILD_BUILD_NUMBER .",
                            "docker tag golang-repository:$CODEBUILD_BUILD_NUMBER {ecr_arn}:$CODEBUILD_BUILD_NUMBER".format(ecr_arn=ecr_arn),
                            "docker push {ecr_arn}:$CODEBUILD_BUILD_NUMBER".format(ecr_arn=ecr_arn)
                        ]
                    }
                }
            }),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0
            )
        )

        build_action = codepipeline_actions.CodeBuildAction(
            action_name="RunBuild",
            project=build_project,
            input=source_output
        )
        pipeline.add_stage(stage_name="Build", actions=[build_action])
