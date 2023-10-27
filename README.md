# GPTalk-Slack

Welcome to GPTalk-Slack, a simple yet effective chatbot backend designed to run on the AWS Lambda service. Currently, it supports Azure OpenAI service only. However, if you're using the official OpenAI API, you can modify the integration code as per your requirements.

# Prerequisites
1. python 3.11
2. poetry
3. make

# Instructions
Here's a step-by-step guide on how to set up and use the chatbot.

## Building
To build the lambda package, run the following command:
``` sh
make build
```
This will generate dist/lambda/lambda.zip, which will later be uploaded to create the Lambda function.

## Creating the lambda function

1. Create a Python 3.11 runtime Lambda function. 
2. Upload dist/lambda/lambda.zip in the code source section.
3. Navigate to Runtime Setting and set the handler to *gptalk-slack.lambda_function.handler*
4. Adjust the general configuration and set the timeout to 30 seconds.
5. In Configuration -> Environment variables, add the required values:
   - OPENAI_API_BASE (Obtainable from Azure OpenAI dashboard)
   - OPENAI_API_ENGINE (Obtainable from Azure OpenAI dashboard)
   - OPENAI_API_KEY (Obtainable from Azure OpenAI dashboard)
   - SLACK_BOT_TOKEN (Obtainable from Slack app configuration)
   - SLACK_SIGNING_SECRET (Obtainable from Azure OpenAI dashboard)

## Creating the API Gateway
1. Create an API on AWS API Gateway.
2. Set up the ANY method and configure it as a Lambda proxy integration. Then, integrate it with the Lambda function you created earlier.
3. Set the integration timeout to 1000ms.
4. In Gateway responses, modify the timeout response status code to 200.

## Setup Slack app

1. Create your own app on Slack (https://api.slack.com/apps)
2. Enable Event Subscriptions and input your API Gateway invoke URL. Then subscribe to the bot event: app_mention
3. In the OAuth & Permissions page -> Bot Token Scopes, ensure the following scopes are included:
   - app_mentions:read
   - chat:write
   - channels:history
   - groups:history
   - im:history
   - mpim:history
4. Install the app to your workspace

## Usage
Mention the chatbot in your workspace and it will respond to you in a separate thread. Each thread operates as a separate conversation context. Enjoy interacting with your new chatbot!

# Future Improvements
- [ ] Support direct message
- [ ] Support OpenAI official API
- [ ] Provide Infra as code script to create lambda function and api gateway


# Note
Slack requires events to respond with a 200 status within 3 seconds; otherwise, Slack's server will attempt to retry thrice. If the Lambda function can't process the event within this timeframe, you may receive multiple replies for a single mention. The Bolt SDK provides a solution in the form of a lazy listener (only for Python version). However, in AWS Lambda, it might take longer than 3 seconds, even with a lazy listener (especially during cold starts). Hence, this project uses a workaround by forcing the API Gateway to timeout within 3 seconds and respond with a 200 status when the integration times out.
