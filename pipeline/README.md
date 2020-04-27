# morphology_pipeline

## Deployment

### Steps

1. Configure the [AWS CLI](https://aws.amazon.com/cli/)
1. Create or retrieve a [GitHub personal access token](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line)
1. Run the `deploy.sh` script in this directory. Uses the following environment variables:
    * `GITHUB_OAUTH` allows CodePipeline to integrate with Github: Use a [GitHub personal access token](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line)
    * `GITHUB_BRANCH` defines the branch to build from. Also used to namespace resources (so make sure the branch name follows [S3 bucket name rules](https://docs.aws.amazon.com/AmazonS3/latest/dev/BucketRestrictions.html)).
    * `GITHUB_OWNER` and `GITHUB_REPO` (optional) define the repository to build from.
    * `STACK_NAME` (optional) will name the root stack which owns the CodePipeline.
    * `PROJECT_NAME` (optional) is used to namespace resources.
    * `AWS_REGION` (optional) deploy to here. Defaults to your currently configured region
    * `AWS_PROFILE` (optional) deploy using this profile. Defauls to your currently configured profile.
