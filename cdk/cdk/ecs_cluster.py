from constructs import Construct

from aws_cdk import (
        Stack,
        aws_ecs as ecs,
        aws_ec2 as ec2
)


class EcsStack(Stack):

    def __init__(self, scope: Construct, id: str, vpc: ec2.IVpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.cluster = ecs.Cluster(self, "MyCluster", vpc=vpc, cluster_name="GolangCluster")
        # Add capacity to it
        self.cluster.add_capacity("DefaultAutoScalingGroupCapacity",
            instance_type=ec2.InstanceType("t2.small"),
            desired_capacity=3
        )

        self.task_definition = ecs.Ec2TaskDefinition(self, "GolangTaskDefinition")

        self.task_definition.add_container("DefaultContainer",
            image=ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample"),
            memory_limit_mib=512
        )

        self.ecs_service = ecs.Ec2Service(self, "GolangServiceService",
            cluster=self.cluster,
            task_definition=self.task_definition
        )
