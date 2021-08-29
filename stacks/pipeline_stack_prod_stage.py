from aws_cdk import core as cdk
from stacks.ab3_stack import Ab3Stack


class PipelineStackProdStage(cdk.Stage):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        ab3_stack = Ab3Stack(self, "Ab3Stack")
        