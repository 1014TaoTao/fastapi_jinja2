from openai import OpenAI


class Agent:

    def __init__(self, base_url, model, api_key):
        self.base_url = base_url
        self.model = model
        self.api_key = api_key

    async def seed_message(self, query: str):

        system_prompt = (
            "You are a helpful assistant."
            "You have the function of online search. "
            "Please MUST call web_search tool to search the Internet content before answering."
            "Please do not lose the user's question information when searching,"
            "and try to maintain the completeness of the question content as much as possible."
            "When there is a date related question in the user's question,"
            "please use the search function directly to search and PROHIBIT inserting specific time."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]

        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False
        )

        result = response.choices[0].message.content

        return result
