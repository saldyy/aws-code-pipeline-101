from constructs import Construct

from aws_cdk import (
        Stack,
        aws_ecs as ecs,
        aws_ec2 as ec2,
        aws_ecr as ecr,
        aws_logs as logs,
        aws_ecs_patterns as ecs_patterns,
        aws_elasticloadbalancingv2 as elbv2,
        RemovalPolicy,
        Duration
)


class EcsStack(Stack):

    def __init__(self, scope: Construct, id: str, vpc: ec2.IVpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # ECR
        repository = ecr.Repository.from_repository_name(self, "GolangRepository",
                                                        repository_name="golang-repository")

        # ECS Cluster
        self.cluster = ecs.Cluster(self, "MyCluster", vpc=vpc, cluster_name="GolangCluster")
        # Add capacity to it
        self.cluster.add_capacity("DefaultAutoScalingGroupCapacity",
            instance_type=ec2.InstanceType("t2.small"),
            machine_image=ecs.EcsOptimizedImage.amazon_linux2(),
            desired_capacity=1,
            min_capacity=1,
            max_capacity=3,
        )


        # CloudWatch Log Group
        log_group = logs.LogGroup(
            self,
            "GolangServiceLogGroup",
            log_group_name="/ecs/application-container-logs",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY
        )
        # ECS Task Definition
        self.task_definition = ecs.Ec2TaskDefinition(
            self,
            "GolangTaskDefinition",
            network_mode=ecs.NetworkMode.AWS_VPC          
            )

        self.task_definition.add_container("DefaultContainer",
            image=ecs.ContainerImage.from_ecr_repository(repository, tag="golang-proj-6"),
            memory_limit_mib=512,
            cpu=256,
            container_name="GolangContainer",
            port_mappings=[ecs.PortMapping(
                container_port=8080,
                protocol=ecs.Protocol.TCP)
            ],
            logging=ecs.LogDriver.aws_logs(stream_prefix="ecs", log_group=log_group)
        )

        service = ecs_patterns.ApplicationLoadBalancedEc2Service(
            self, "GolangApplicationService",
            cluster=self.cluster,
            task_definition=self.task_definition,
            desired_count=1,
            public_load_balancer=True,
            listener_port=80,
            target_protocol=elbv2.ApplicationProtocol.HTTP,
            deployment_controller=ecs.DeploymentController(type=ecs.DeploymentControllerType.CODE_DEPLOY),
        )

        # Customize the health check on the target group
        service.target_group.configure_health_check(
            path="/",
            port="8080",
            healthy_http_codes="200",
            interval=Duration.seconds(30),
            timeout=Duration.seconds(5),
            healthy_threshold_count=2,
            unhealthy_threshold_count=3,
        )
