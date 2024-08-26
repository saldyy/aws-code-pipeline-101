from constructs import Construct

from aws_cdk import (
    Stack,
    CfnOutput, 
    aws_codestarconnections as codestarconnections
) 

class PipelineStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create the CodeStar Connection
        codestar_connection = codestarconnections.CfnConnection(
            self, "SaldyyGitHubConnection",
            connection_name="SaldyyGitHubConnection",  # Connection name
            provider_type="GitHub"  # The third-party provider (e.g., GitHub, Bitbucket)
        )
        codestarconnections.CfnRepositoryLink(self, "SaldyyCfnRepositoryLink",
            connection_arn=codestar_connection.attr_connection_arn,
            owner_id="saldyy",
            repository_name="code-pipeline-101",
        )


        # Output the ARN of the connection
        CfnOutput(self, "ConnectionArn", value=codestar_connection.attr_connection_arn)

