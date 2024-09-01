from aws_cdk import (CfnOutput, Stack, aws_ec2)
from constructs import Construct


class VpcStack(Stack):

    def __init__(self, scope: Construct, id, **kwargs):
        super().__init__(scope, id, **kwargs)
        # Create VPC
        self.vpc = aws_ec2.Vpc(
            self,
            id="GolangVpc",
            cidr="10.0.0.1/16",
            availability_zones=[
                "ap-southeast-1a",
                "ap-southeast-1b",
                "ap-southeast-1c"
            ]
        )

        CfnOutput(self, "VpcId", value=self.vpc.vpc_id)
