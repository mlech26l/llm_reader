import openai
import os

from llm_api import LLM

SYSTEM_PROMPT = "You are a helpful AI assistant that rephrases text into a \
different style that your user prefers. \
Never output the input text without any modification. \
Only rephrase the next, do not provide more information beyond the user content. \
For instance, the user may request the documented to be rephrased into a more engaging or simpler langauge. \
Your output should only contain the modified original text without any confirmation of the request or further question. \
Note that the text may contain text artifacts from parsing the document, simply ignore them."


class Personalizer:
    def __init__(self, content):
        self.content = content
        self.style = ""
        self.model = "chatgpt"
        self.pointer_start = 0
        self.pointer_end = 0
        self.advance_end_pointer()
        self._styled_section = None
        self.llm = LLM()
        self.pointer_stack = []

    def set_model(self, model):
        self.model = model.lower().replace("-", "").strip()

    def set_style(self, style):
        self.style = style
        self._styled_section = None

    @property
    def section(self):
        return self.content[self.pointer_start : self.pointer_end]

    def query_styled_selection(self, callback):
        if self.style == "":
            print("[Peronalizer]: No style set, returning original text")
            callback(self.section)
        else:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "Rephrase preference: " + self.style},
                {"role": "user", "content": "Content to rephrase: " + self.section},
            ]
            print("[Peronalizer]: Querying LLM for styled selection")
            self.llm.query(self.model, messages, callback)

    def advance_section(self):
        self.pointer_stack.append(self.pointer_start)
        self.pointer_start = self.pointer_end
        self.advance_end_pointer()
        print(
            f"[Peronalizer]: Advancing section {self.pointer_start} - {self.pointer_end}"
        )

    def retreat_section(self):
        if len(self.pointer_stack) == 0:
            return
        self.pointer_end = self.pointer_start
        self.pointer_start = self.pointer_stack.pop()
        print(
            f"[Peronalizer]: Retreating section {self.pointer_start} - {self.pointer_end}"
        )

    def advance_end_pointer(self):
        words = 0
        chars = 0
        while self.pointer_end < len(self.content) and words < 400 and chars < 30000:
            if self.content[self.pointer_end] == " ":
                words += 1
            self.pointer_end += 1
            chars += 1