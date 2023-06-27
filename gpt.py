import openai
import tiktoken
import json
import os


class SimpleGPT:

    name = "gpt"
    api_key = "API KEY NEEDED"
    api_model = "gpt-3.5-turbo"
    api_system_role = """You are an assistant."""
    api_tokens = 2000
    reflection_iterations = 0

    def __init__(self, inital_prompt=None, stream: bool = False, file: str = None) -> None:
        ''' Creates a SimpleGPT instance, allowing for easy conversations.'''
        openai.api_key = self.api_key
        self.system = {"role": "system",
                       "content": self.api_system_role}
        self.backup = None
        self.stream = False
        self.messages = []
        if file is not None:
            self.__load_conversation(file)
        elif inital_prompt is not None:
            self.respond(inital_prompt)

    def __call__(self, prompt: str) -> str:
        return self.respond(prompt)

    def __load_conversation(self, file: str) -> list:
        ''' Creates a context-based chat, which OpenAI API does not support natively '''
        assert os.path.exists(str), "File must be an actual path!"

    def __str__(self) -> str:
        return json.dumps(self.messages)

    def get_last_message(self, index: int = 1) -> str:
        ''' Returns the last / newest message on the list '''
        return self.messages[-index]

    def respond(self, answer, user='user'):
        ''' Responds in the conversation '''
        self.messages.append({"role": user, "name": user, "content": answer})
        return self.api_call()

    def number_tokens(self, model=api_model):
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")

        if model == "gpt-3.5-turbo":
            print(
                "Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
            return self.number_tokens(model="gpt-3.5-turbo-0301")
        elif model == "gpt-4":
            print(
                "Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
            return self.number_tokens(model="gpt-4-0314")
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4
            tokens_per_name = -1
        elif model == "gpt-4-0314":
            tokens_per_message = 3
            tokens_per_name = 1
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")

        full_messages = [self.system] + self.messages
        num_tokens = 0
        for msg in full_messages:
            num_tokens += tokens_per_message
            for key, value in msg.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

    def reflect(self, ite: int = reflection_iterations, store: bool = False) -> str:
        ''' Asks GPT if it's sure. Sometimes it converges towards the right answer
            n : denotes number of reflect iterations
            store : store reflection messaging in messages? (default: False)
        '''
        success = False
        # Check if the reflection should be stored
        if not store:
            assert self.backup is None
            self.backup = self.messages.copy()
        # Run reflection n times (defined in apps.py)
        for _ in range(ite):
            self.respond(self.api_reflection_string)
            last = self.get_last_message()["content"]
            if last.lower().startswith("yes"):
                success = True
                break
        # Restore original messages if not to be stored
        if not store:
            if success:
                last_msg = self.get_last_message(index=3)
            self.messages = self.backup.copy()
            if success:
                self.messages.append(last_msg)
            self.backup = None
        # Return success
        return success

    def add_stream_response(self, addStr: str):
        self.messages.append(
            {"role": "assistant", "content": addStr})

    def api_call(self,  model: str = api_model) -> str:
        print("API CALL MADE")
        ''' 
        Takes in text and forwards it to a specified OpenAPI GPT engine,
        by default GPT-3.5 by default. The specification of the settings can
        be changed in apps.py
        '''

        # Make sure the number of tokens are within the limits
        for _ in range(len(self.messages)):
            if self.number_tokens() - self.api_tokens > 0:
                self.messages.pop()
            else:
                break

        # Prepend the system message to our messages
        convo = [self.system] + self.messages

        # If message is not empty, make API call
        try:
            if len(self.messages) != 0:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=convo,
                    temperature=0.5,
                    max_tokens=self.api_tokens,
                    top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=0.0,
                    stream=True
                )

                return response
            else:
                raise IndexError("Messages are too long or empty!")
        except Exception as err:
            raise err
