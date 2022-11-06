"""AWS CDK module to create ECS infrastructure"""
from aws_cdk import (Stack, aws_ecs as ecs, aws_ecr as ecr, aws_ec2 as ec2, aws_iam as iam, RemovalPolicy)
from constructs import Construct

class EcsDevopsSandboxCdkStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create the ECR Repository
        ecr_repository = ecr.Repository(self,
                                        "ecs-devops-sandbox-repository",
                                        repository_name="ecs-devops-sandbox-repository")

        # Create the ECS Cluster (and VPC)
        vpc = ec2.Vpc(self,
                      "ecs-devops-sandbox-vpc",
                      max_azs=3)
        cluster = ecs.Cluster(self,
                              "ecs-devops-sandbox-cluster",
                              cluster_name="ecs-devops-sandbox-cluster",
                              vpc=vpc)

        # Create the ECS Task Definition with placeholder container (and named Task Execution IAM Role)
        execution_role = iam.Role(self,
                                  "ecs-devops-sandbox-execution-role",
                                  assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
                                  role_name="ecs-devops-sandbox-execution-role")
        execution_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=["*"],
            actions=[
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:CreateLogGroup"
                ]
        ))
        task_definition = ecs.FargateTaskDefinition(self,
                                                    "ecs-devops-sandbox-task-definition",
                                                    execution_role=execution_role,
                                                    family="ecs-devops-sandbox-task-definition")
        container = task_definition.add_container(
            "ecs-devops-sandbox",
            image=ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample"),
            logging=ecs.LogDriver.aws_logs(stream_prefix="batch"),
        )

        sg = ec2.SecurityGroup(self, 
                                "ecs-devops-sandbox-sg",
                                security_group_name="ecs-devops-sandbox-sg",
                                vpc=vpc
                                )

        sg.add_ingress_rule(ec2.Peer.any_ipv4(),  
                            ec2.Port.tcp(8080),
                            'Allow access on port 8080')


        # Create the ECS Service
        # service = ecs.FargateService(self,
        #                              "ecs-devops-sandbox-service",
        #                              cluster=cluster,
        #                              task_definition=task_definition,
        #                              service_name="ecs-devops-sandbox-service",
        #                              assign_public_ip=True,
        #                              security_groups=[sg])