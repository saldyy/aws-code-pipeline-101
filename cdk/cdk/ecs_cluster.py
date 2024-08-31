from aws_cdk.aws_ec2 import IVpc
from constructs import Construct

from aws_cdk import Stack, aws_ecs as ecs


class EcsStack(Stack):

    def __init__(self, scope: Construct, id: str, vpc: IVpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create ECS cluster
        ecs.Cluster(self, "MyCluster", vpc=vpc, cluster_name="GolangCluster")
