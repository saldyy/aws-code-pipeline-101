from aws_cdk.aws_ecs import IService, ITaskDefinition
from aws_cdk.aws_ecs_patterns import ApplicationLoadBalancedEc2Service, ApplicationLoadBalancedEc2ServiceProps
from constructs import Construct

from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_ecr,
    RemovalPolicy,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codedeploy as codedeploy,
    aws_elasticloadbalancingv2 as elbv2
)

class PipelineStack(Stack):

    def __init__(self, scope: Construct, id: str, connection_arn: str, task_definition: ITaskDefinition,
                 ecs_service: ApplicationLoadBalancedEc2Service, repository: aws_ecr.IRepository,**kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        code_build_access_role = iam.Role(
                self,
                "CodeBuildRole",
                assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
                role_name="code-build-role"
            )
        code_build_access_role.add_to_policy(iam.PolicyStatement(
            actions=[
                "ecs:DescribeTaskDefinition",
                "ecs:RegisterTaskDefinition",
                "ecs:ListTaskDefinitions",
             ],
            resources=["*"]
        ))

        repository.grant_pull_push(code_build_access_role)


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
            role=code_build_access_role,
            build_spec=codebuild.BuildSpec.from_object({
                "version": 0.2,
                "phases": {
                    "build": {
                        "commands": [
                            "echo --------START BUILD--------",
                            "cd app",
                            "IMAGE_TAG=golang-proj-$CODEBUILD_BUILD_NUMBER",
                            "aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin {ecr_uri}".format(ecr_uri=repository.repository_uri),
                            "docker build -t $IMAGE_TAG .",
                            "docker tag $IMAGE_TAG {ecr_uri}:$IMAGE_TAG".format(ecr_uri=repository.repository_uri),
                            "docker push {ecr_uri}:$IMAGE_TAG".format(ecr_uri=repository.repository_uri)
                        ]
                    },
                    "post_build": {
                        "commands": [
                            "echo --------START POST BUILD--------",
                            "IMAGE_TAG=golang-proj-$CODEBUILD_BUILD_NUMBER",
                            "IMAGE_URI={ecr_uri}:$IMAGE_TAG".format(ecr_uri=repository.repository_uri),
                            "aws ecs describe-task-definition --task-definition ${TASK_DEFINITION_NAME} | jq '.taskDefinition.containerDefinitions[0].image = \"\'\"$IMAGE_URI\"\'\"' > temp.json", "jq '.taskDefinition' temp.json > taskdef.json",
                            "cat taskdef.json",
                        ]

                    }
                },
                "artifacts": {
                    "files": ["app/appspec.yaml", "app/taskdef.json"]
                }
            }),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                environment_variables = {
                    "TASK_DEFINITION_NAME": codebuild.BuildEnvironmentVariable(value="EcsgolangcicdGolangTaskDefinitionCF434C82")
                }
            ),
        )

        build_output = codepipeline.Artifact(artifact_name="BuildArtifact")
        build_action = codepipeline_actions.CodeBuildAction(
            action_name="RunBuild",
            project=build_project,
            input=source_output,
            outputs=[build_output]
        )
        pipeline.add_stage(stage_name="Build", actions=[build_action], )


        code_deploy_role = iam.Role(
            self,
            "CodeDeployRole",
            assumed_by=iam.ServicePrincipal("codedeploy.amazonaws.com"),
            role_name="code-deploy-role",
        )
        code_deploy_role.add_to_policy(iam.PolicyStatement(
            actions=[
                "ecs:DescribeServices",
                "ecs:UpdateService",
                "ecs:DescribeTaskDefinition",
                "ecs:RegisterTaskDefinition",
                "iam:PassRole",
                "codedeploy:*",
            ],
            resources=[task_definition.task_definition_arn]
        ))

        deploy_application = codedeploy.EcsApplication(
            self,
            "CodeDeployApplication",
            application_name="GolangDeployApplication",
        )
        green_target_group = elbv2.ApplicationTargetGroup(self, "GreenTargetGroup",
                                                          vpc=ecs_service.cluster.vpc, port=80,
                                                          target_type=elbv2.TargetType.IP)
        deployment_group = codedeploy.EcsDeploymentGroup(
            self,
            "BlueGreenDeployDeploymentGroup",
            role=code_deploy_role,
            auto_rollback=codedeploy.AutoRollbackConfig(stopped_deployment=True),
            application=deploy_application,
            service=ecs_service.service,
            deployment_config=codedeploy.EcsDeploymentConfig.ALL_AT_ONCE,
            blue_green_deployment_config=codedeploy.EcsBlueGreenDeploymentConfig(
                blue_target_group=ecs_service.target_group,
                green_target_group=green_target_group,
                listener=ecs_service.listener,
            ),
        )

        deploy_action = codepipeline_actions.CodeDeployEcsDeployAction(
            action_name="Deploy",
            deployment_group=deployment_group,
            task_definition_template_file=codepipeline.ArtifactPath(build_output, file_name="app/taskdef.json"),
            app_spec_template_file=codepipeline.ArtifactPath(build_output, file_name="app/appspec.yaml"),
        )
        pipeline.add_stage(stage_name="Deploy", actions=[deploy_action])
