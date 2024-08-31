from aws_cdk import (CfnOutput, Stack, aws_ec2)
from constructs import Construct


class VpcStack(Stack):

    def __init__(self, scope: Construct, id, **kwargs):
        super().__init__(scope, id, **kwargs)
        # Create VPC
        self.vpc = aws_ec2.Vpc(
            self, "GolangVpc",
            max_azs=1
        )

        CfnOutput(self, "VpcId", value=self.vpc.vpc_id)
