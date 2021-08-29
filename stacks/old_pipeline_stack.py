from aws_cdk import core as cdk
import aws_cdk.aws_codepipeline as cp
import aws_cdk.aws_iam as iam


class PipelineStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        self.cp_iam_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "*",
                    "Resource": "*"
                }
            ]
        }

        self.cp_iam_role_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowFlowLogs",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "codepipeline.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }

        self.cp_iam_role = iam.CfnRole(self,
            id='CodePipeline IAM Role',
            description='CodePipeline IAM Role',
            path='/',
            assume_role_policy_document=self.cp_iam_role_policy,
            policies=[
                {
                    "policyName": "codepipeline-iam-role",
                    "policyDocument": self.cp_iam_policy
                }
            ]
        )

        self.cdk_pipeline = cp.CfnPipeline(self,
            id='CDK Pipeline',
            role_arn=self.cp_iam_role.attr_arn,
            artifact_store=cp.CfnPipeline.ArtifactStoreProperty(
                type='S3',
                location='awstomburge-github-artifact-store'
            ),
            stages=[
                cp.CfnPipeline.StageDeclarationProperty(
                    name='Source',
                    actions=[
                        cp.CfnPipeline.ActionDeclarationProperty(
                            name='Source',
                            action_type_id=cp.CfnPipeline.ActionTypeIdProperty(
                                category='Source',
                                owner='ThirdParty',
                                version='2',
                                provider='GitHub'
                            ),
                            configuration={
                                "Owner" : "awstomburge",
                                "Repo" : "cdk-pipelines-demo-python",
                                "Branch" : "main",
                                "OAuthToken" : "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",
                                "PollForSourceChanges" : True
                            },
                            output_artifacts=[
                                cp.CfnPipeline.OutputArtifactProperty(
                                    name='SourceOutput'
                                )
                            ]
                        )
                    ]
                )
            ]
        )