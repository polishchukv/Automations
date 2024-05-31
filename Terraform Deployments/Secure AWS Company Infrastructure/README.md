# AWS Infrastructure with Terraform

## Table of Contents

- [Introduction](#introduction)
- [Files Overview](#files-overview)
  - [main.tf](#maintf)
  - [variables.tf](#variablestf)
  - [outputs.tf](#outputstf)
- [Functionality](#functionality)
  - [VPC and Subnets](#vpc-and-subnets)
  - [Security Groups](#security-groups)
  - [IAM Roles and Policies](#iam-roles-and-policies)
  - [EC2 Instances](#ec2-instances)
  - [KMS Key](#kms-key)
  - [Secrets Manager](#secrets-manager)
  - [RDS Instance](#rds-instance)
  - [CloudTrail](#cloudtrail)
- [Setup and Deployment](#setup-and-deployment)
  - [Prerequisites](#prerequisites)
  - [Steps to Deploy](#steps-to-deploy)
- [Outputs](#outputs)
- [Cleanup](#cleanup)
- [Conclusion](#conclusion)

## Introduction

This project uses Terraform to provision a secure, scalable AWS infrastructure. The infrastructure includes a Virtual Private Cloud (VPC) with public and private subnets, EC2 instances for various purposes (including DMZ and internal servers), an optional RDS instance for database management, and enhanced security measures such as IAM roles, KMS encryption, and Secrets Manager for secure credential storage. CloudTrail is also enabled for auditing and monitoring.

## Files Overview

### main.tf

The `main.tf` file contains the primary Terraform configuration for this project. It includes the definitions for the VPC, subnets, security groups, IAM roles and policies, EC2 instances, KMS key, Secrets Manager, RDS instance, and CloudTrail setup.

### variables.tf

The `variables.tf` file is used to define input variables that are used in the `main.tf` file. This allows for parameterization and easier customization of the Terraform configuration.

### outputs.tf

The `outputs.tf` file defines the outputs that Terraform will provide after the infrastructure is created. These outputs include important information such as the public and private IP addresses of the EC2 instances.

## Functionality

### VPC and Subnets

The VPC and subnets are the foundational components of the AWS infrastructure. They define the network topology and segmentation.

- **VPC**: A Virtual Private Cloud that provides an isolated network environment.
- **Public Subnet**: A subnet within the VPC that has access to the internet via an Internet Gateway.
- **Private Subnet**: A subnet within the VPC that does not have direct internet access.

### Security Groups

Security groups act as virtual firewalls to control inbound and outbound traffic for AWS resources.

- **User Security Group**: Allows SSH access from anywhere.
- **DMZ Security Group**: Allows HTTP access from anywhere.
- **Internal Security Group**: Allows SSH access from the public subnet.
- **Enhanced Security Group**: Allows HTTPS access from anywhere.

### IAM Roles and Policies

IAM roles and policies are used to manage permissions for AWS resources.

- **EC2 Role**: A role that EC2 instances assume to gain specific permissions.
- **EC2 Policy**: A policy that grants permissions for EC2 instances to describe resources and list S3 buckets.

### EC2 Instances

EC2 instances are virtual servers in the AWS cloud.

- **DMZ Server**: An EC2 instance in the public subnet for handling external traffic.
- **Internal Servers**: EC2 instances in the private subnet for internal use.
- **Bastion Host**: An EC2 instance in the public subnet for secure access to the private subnet.

### KMS Key

KMS (Key Management Service) is used to encrypt data.

- **KMS Key for RDS**: Encrypts the RDS database instance to enhance security.

### Secrets Manager

Secrets Manager is used to securely store sensitive information such as database credentials.

- **DB Credentials**: Stores the username and password for the RDS instance.

### RDS Instance

RDS (Relational Database Service) provides a managed database service.

- **RDS Instance**: A MySQL database instance with encryption enabled using KMS.

### CloudTrail

CloudTrail is used for monitoring and auditing API calls made within the AWS account.

- **CloudTrail Setup**: Configures CloudTrail to log all API calls and store logs in an S3 bucket.

## Setup and Deployment

### Prerequisites

- AWS account with appropriate permissions.
- AWS CLI installed and configured.
- Terraform installed.

### Steps to Deploy

1. **Clone the Repository**:
   ```sh
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Initialize Terraform**:
    ```sh
    terraform init
    ```

3. **Review & Customize Variables**:
    Edit `variables.tf` as needed to customize configuration.
    Can be left as default.

4. **Plan Deployment**:
    ```sh
    terraform plan
    ```

5. **Apply Configuration**:
    ```sh
    terraform apply
    ```

6. **Verify Deployment**:
    Check the AWS Management Console to ensure resource have been created as expected.

## Outputs

After the deployment, Terraform will provide the following outputs:

- **DMZ Instance Public IP**: The public IP address of the DMZ server.
- **Internal Instance #1 Private IP**: The private IP address of Internal Server #1.
- **Internal Instance #2 Private IP**: The private IP address of Internal Server #2.
- **Internal Instance #3 Private IP**: The private IP address of Internal Server #3.
- **Bastion Instance Public IP**: The public IP address of the Bastion Host.

## Cleanup

To destroy the infrastructure and clean up resources:
```sh
terraform destroy
```