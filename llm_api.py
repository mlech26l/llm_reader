import openai
import os
import threading


def hash_messages(messages):
    return hash("\n".join([r + ": " + m for r, m in messages]))


class LLM:
    def __init__(self, model="gpt-3.5-turbo"):
        # if "OPENAI_ORG" not in os.environ or "OPENAI_API_KEY" not in os.environ:
        #     raise Exception(
        #         "Missing OPENAI_ORG or OPENAI_API_KEY environment variable."
        #     )
        # openai.organization = os.getenv("OPENAI_ORG")
        # openai.api_key = os.getenv("OPENAI_API_KEY")
        self.model_name = model
        self._cached_replies = {}

    def call_llm(self, args):
        messages, key, callback = args
        response = openai.ChatCompletion.create(
            model=self.model_name, messages=messages
        )
        reply = response["choices"][0]["message"][-1]["content"]
        self._cached_replies[key] = reply
        callback(reply)

    def query(self, messages, callback):
        key = hash_messages(messages)
        if key in self._cached_replies:
            print("cached reply")
            callback(self._cached_replies[key])
        else:
            style = messages[-2]["content"]
            content = messages[-1]["content"]
            # content = content[0 : min(len(content), 1000)]
            print("calling fake llm")
            callback("Placeholder text with style " + style + " and content " + content)
            #
            # thread = threading.Thread(
            #     target=self.call_llm,
            #     args=(messages, key, callback),
            # )
            # thread.start()