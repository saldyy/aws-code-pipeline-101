from constructs import Construct

from aws_cdk import (
    Stack,
    pipelines
) 

class PipelineStack(Stack):

    def __init__(self, scope: Construct, id: str, connection_arn: str,**kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        pipeline = pipelines.CodePipeline(self, "Pipeline",
            synth=pipelines.ShellStep("Synth",
                input=pipelines.CodePipelineSource.connection("/aws-code-pipeline-101",
                                                              "master",
                                                              connection_arn=connection_arn),
                commands=["make build"]
            )
        )


