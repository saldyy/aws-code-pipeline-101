from constructs import Construct

from aws_cdk import (
    Stack,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,

) 

class PipelineStack(Stack):

    def __init__(self, scope: Construct, id: str, connection_arn: str,**kwargs) -> None:
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


