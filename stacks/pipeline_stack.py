from aws_cdk import core as cdk
from aws_cdk import aws_codepipeline as codepipeline
import aws_cdk.pipelines as pipelines
from stacks.pipeline_stack_test_stage import PipelineStackTestStage


class PipelineStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        self.code_pipeline = pipelines.CodePipeline(self,
            id='CDK Pipeline',
            self_mutation=True,
            synth=pipelines.ShellStep(
                id='Synth',
                input=pipelines.CodePipelineSource.git_hub(
                    'awstomburge/cdk-pipelines-demo-python',
                    'main',
                    authentication=cdk.SecretValue.secrets_manager('awstomburge-github-token')
                ),
                commands=["npm install -g aws-cdk", "pip install -r requirements.txt", "cdk synth"]
            )
        )

        self.code_pipeline.add_stage(PipelineStackTestStage(self, "Test-Deploy"))


