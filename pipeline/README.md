Deploying the neuron morphology pipeline
========================================

This document explains how to deploy the neuron morphology pipeline - an AWS application which uses the `neuron_morphology` package to process single-neuron morphological reconstructions.

## Prerequisites

1. Configure the [AWS CLI](https://aws.amazon.com/cli/)
1. Create or retrieve a [GitHub personal access token](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line)

## Persistent resources

This one-time-only step sets up longstanding shared resources, such as a repository for docker images. If someone on your team has already done this, you can go to the next section.

To deploy the persistent resources, pick a stack name and run:
```
aws cloudformation deploy \
    --stack-name <your stack name> \
    --template-file pipeline/deploy/cloudformation/persistent.yml
```

Note the stack name that you used. You will reference it in later sections.

## CI/CD via CodePipeline

In this section, you will deploy a CI/CD stack for a single git branch. This stack will own a namespaced copy of the neuron morphology pipeline. On commit to the specified branch, it will update that copy of the pipeline with the changes.

To deploy the CI/CD stack, you can use the `deploy.sh` script in this directory. You will need to provide (as environment variables):
* `GITHUB_OAUTH` allows CodePipeline to integrate with Github: Use a [GitHub personal access token](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line)
* `GITHUB_BRANCH` defines the branch to build from.
* `STACK_NAME` a name for this new CI/CD stack (and used to prefix deriviative resources)
* `PERSISTENT_STACK_NAME` The name of the persistent stack from the previous section. This tells your pipeline where to store e.g. its build artifacts.

You may also provide these optional arguments:
* `GITHUB_OWNER` and `GITHUB_REPO` define the repository to build from.
* `PROJECT_NAME` is used to namespace resources.
* `AWS_REGION`deploy to here. Defaults to your currently configured region
* `AWS_PROFILE` deploy using this profile. Defauls to your currently configured profile.
* `BRANCH_TYPE` one of "dev" (default), "stage", or "prod". This determines how long your build artifacts are kept around.
