from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler
from typing import List, Dict
import logging
import re
import openai
import os

openai.api_type = "azure"
openai.api_version = "2023-07-01-preview"
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_key = os.getenv("OPENAI_API_KEY")
openai_engine = os.getenv("OPENAI_API_ENGINE")

LOG = logging.getLogger()
LOG.setLevel("INFO")
app = App(process_before_response=True)
mention_pattern = re.compile(r"<@.*?>")
past_message_include = 10


@app.event("app_mention")
def handle_app_mentions(body: dict, say, logger):
    logger.info(body)
    channel = body["event"].get("channel", None)
    if not channel:
        logger.warn("channel is None!")
        return
    ts = body["event"].get("ts", None)
    thread_ts = body["event"].get("thread_ts", None)
    bot_user_id = body["authorizations"][0]["user_id"]

    reply = get_response(
        replies_context=get_thread_context(
            channel, thread_ts, bot_user_id, current_mention_text=body["event"]["text"]
        )
    )

    blocks = [
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": reply,
                }
            ],
        }
    ]
    say(text="", blocks=blocks, thread_ts=thread_ts or ts)


def get_thread_context(
    channel: str, ts: str, bot_user_id: str, current_mention_text: str
) -> List[Dict[str, str | bool]]:
    if not ts:
        return [
            {
                "text": remove_user_mention_part(current_mention_text),
                "is_bot": False,
            }
        ]
    data: dict = app.client.conversations_replies(channel=channel, ts=ts).data  # type: ignore
    LOG.info(data)
    messages = data["messages"] or []
    plain_text = [
        {
            "text": remove_user_mention_part(msg["text"]),
            "is_bot": msg["user"] == bot_user_id,
        }
        for msg in messages
        if msg["text"]
        and (f"<@{bot_user_id}>" in msg["text"] or msg["user"] == bot_user_id)
    ]
    return plain_text


def get_response(replies_context: List[Dict[str, str | bool]]) -> str:
    messages = [
        {
            "role": "system",
            "content": "You are an AI assistant that helps people find information. You should respond in markdown format.",
        }
    ] + [
        {"role": "assistant" if msg["is_bot"] else "user", "content": msg["text"]}
        for msg in replies_context[-past_message_include:]
    ]
    LOG.info(messages)

    response = openai.ChatCompletion.create(
        engine=openai_engine,
        messages=messages,
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
    )
    return response.choices[0].message.content  # type: ignore


def remove_user_mention_part(string):
    return re.sub(mention_pattern, "", string).strip()


def handler(event, context):
    return SlackRequestHandler(app=app).handle(event, context)
