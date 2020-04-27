#!/bin/bash

set -euxo pipefail

STACK_NAME=${STACK_NAME:-morphology_codepipeline_ci}
PROJECT_NAME=${PROJECT_NAME:-morphology-processing-pipeline}

GITHUB_REPO=${GITHUB_REPO:-neuron_morphology}
GITHUB_BRANCH=${GITHUB_BRANCH:-dev}
GITHUB_OWNER=${GITHUB_OWNER:-AllenInstitute}

DIR=$(dirname  "$(readlink -f "$0")")

AWS_PROFILE=${AWS_PROFILE:-$(aws configure get profile)}
AWS_REGION=${AWS_REGION:-$(aws configure get region)}

aws cloudformation deploy --stack-name $STACK_NAME  --template-file $DIR/deploy/cloudformation/codepipeline/cfn_pipeline.yml \
    --profile $AWS_PROFILE \
    --region $AWS_REGION \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides \
    GitHubOAuthToken=$GITHUB_OAUTH \
    GitHubRepoOwner=$GITHUB_OWNER \
    GitHubRepo=$GITHUB_REPO \
    GitHubBranch=$GITHUB_BRANCH \
    ProjectName=$PROJECT_NAME