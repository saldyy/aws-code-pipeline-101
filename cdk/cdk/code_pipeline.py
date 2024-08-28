from typing_extensions import runtime
from constructs import Construct

from aws_cdk import (
    Stack,
    pipelines,
    Stage
) 

class TestStageStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

class TestStage(Stage):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        TestStageStack(self, "TestStageStack")

class PipelineStack(Stack):

    def __init__(self, scope: Construct, id: str, connection_arn: str,**kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        pipeline = pipelines.CodePipeline(self, "Pipeline",
            synth=pipelines.ShellStep("Synth",
                input=pipelines.CodePipelineSource.connection("saldyy/aws-code-pipeline-101",
                                                              "master",
                                                              connection_arn=connection_arn),
                commands=["pip install -r requirements.txt", "npm install -g aws-cdk", "cdk synth"],
                primary_output_directory="cdk"
            )
        )
        test_stage = TestStage(self, "Test")
        pipeline.add_stage(test_stage, pre=[
                pipelines.ManualApprovalStep("Approve")
            ])


