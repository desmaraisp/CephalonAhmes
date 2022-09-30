from src import main
from awslambdaric import lambda_context

def lambda_handler(event, context: lambda_context.LambdaContext):
    main.main(AWS_Request_ID=context.aws_request_id)
