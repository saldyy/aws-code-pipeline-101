# Golang Application with AWS ECS Deployment and CI/CD Pipeline

This repository contains:
- A simple Golang application
- AWS CDK project to deploy the application into Amazon ECS with EC2 provider
- Automation CI/CD pipeline using AWS CodePipeline with Blue/Green Deployment

## Prerequisites

Make sure you have the following installed:
- [Golang](https://golang.org/doc/install)
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
- [AWS CDK](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html)
- [Docker](https://docs.docker.com/get-docker/) (for ECS EC2 deployments)
- [Python3](https://www.python.org/) (for AWS CDK)

Ensure that your AWS account is properly configured, and you've set up the appropriate credentials using `aws configure`.

## Project Structure
/app  
├── main.go                 # Simple Golang application  
├── Dockerfile              # Dockerfile to containerize the application  
├── Makefile                # For building and running the application locally  

/cdk  
├── cdk.json                # AWS CDK configuration  
├── bin/  
├── lib/  
└── stack.ts                # CDK stack for ECS, EC2 provider, and CodePipeline (Blue/Green Deployment)

