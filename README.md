# Async Job Processing with Concurrency Limit

This project implements an async job processing system with a configurable concurrency limit per user using AWS services.

## Prerequisites

- AWS CLI installed and configured
- AWS SAM CLI installed
- Python 3.9 or later

## Deployment

1. Clone this repository:

```bash
git clone <repository-url> cd <repository-directory>
```

2. Build the SAM application:

```bash
sam build
```

3. Deploy the SAM application:

```bash
sam deploy --guided
```

Follow the prompts to configure the deployment. Make sure to set the `NumOfConcurrentJobs` parameter to your desired value (default is 5).

4. Note the API Gateway endpoint URL from the deployment output.

## Testing

To test the solution, you can use a tool like `curl` or Postman to send POST requests to the API Gateway endpoint.

Example using curl:

```bash
curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/Prod/submit-job \
-H "Content-Type: application/json" \
-d '{"delay": 10, "user_id": "test-user-1"}'
```

Send multiple requests with the same user_id to test the concurrency limit. You should receive a 429 error when the limit is reached.

## Cleanup

To remove all resources created by this project:

```bash
sam delete
```

Follow the prompts to confirm the deletion of resources.
