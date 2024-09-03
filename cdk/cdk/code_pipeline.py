from constructs import Construct

from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_ecr,
    RemovalPolicy,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,

) 

class PipelineStack(Stack):

    def __init__(self, scope: Construct, id: str, connection_arn: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        repository = aws_ecr.Repository(
                self,
                id="GolangRepository",
                repository_name="golang-repository",
                image_scan_on_push=False,
                removal_policy=RemovalPolicy.DESTROY
                )

        ecr_access_role = iam.Role(
                self,
                "EcrAccessRole",
                assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
                role_name="ecr-access-role"
                )

        repository.grant_pull_push(ecr_access_role)


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
        # pipeline.add_stage(stage_name="Test", actions=[test_action])


        build_project = codebuild.PipelineProject(
            self, "GolangBuildProject",
            role=ecr_access_role,
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
        pipeline.add_stage(stage_name="Build", actions=[build_action])
