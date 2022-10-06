from src import main
from awslambdaric import lambda_context
import typing

def lambda_handler(event: typing.Dict, context: lambda_context.LambdaContext) -> None:
    main.main(AWS_Request_ID=context.aws_request_id)
