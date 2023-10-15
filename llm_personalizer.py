import openai
import os

from llm_api import LLM

SYSTEM_PROMPT = "You are a helpful AI assistant that translates and rephrases text into a \
different style that your user prefers. \
For instance, the user may request the documented to be rephrased into a more engaging or simpler langauge. \
Your output should only contain the modified original text without any confirmation of the request or further question. \
Note that the text may contain text artifacts from parsing the document, simply ignore them."


class Personalizer:
    def __init__(self, content):
        self.content = content
        self.style = ""
        self.pointer_start = 0
        self.pointer_end = 0
        self.advance_end_pointer()
        self._styled_section = None
        self.llm = LLM()
        self.pointer_stack = []

    def set_style(self, style):
        self.style = style
        self._styled_section = None

    @property
    def section(self):
        return self.content[self.pointer_start : self.pointer_end]

    def query_styled_selection(self, callback):
        if self._styled_section is not None:
            print("no style selection -> callback with main text")
            callback(self.section)
        else:
            print("style selection not none -> compute styled section")
            self._styled_section = self._compute_styled_section(callback)

    def _compute_styled_section(self, callback):
        if self.style == "":
            print("empty style -> callback with main text")
            callback(self.section)
        else:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "system", "content": self.style},
                {"role": "user", "content": self.section},
            ]
            print("sending messages to llm:")
            self.llm.query(messages, callback)

    def advance_section(self):
        self.pointer_stack.append(self.pointer_start)
        self.pointer_start = self.pointer_end
        self.advance_end_pointer()
        self._styled_section = None
        print(f"Section {self.pointer_start} - {self.pointer_end}")

    def retreat_section(self):
        if len(self.pointer_stack) == 0:
            return
        self.pointer_end = self.pointer_start
        self.pointer_start = self.pointer_stack.pop()
        self._styled_section = None

    def advance_end_pointer(self):
        words = 0
        chars = 0
        while self.pointer_end < len(self.content) and words < 150 and chars < 20000:
            if self.content[self.pointer_end] == " ":
                words += 1
            self.pointer_end += 1
            chars += 1