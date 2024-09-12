# OpenAIGenerator.py
import os
from dotenv import load_dotenv
from goldenverba.components.interfaces import Generator
from goldenverba.components.types import InputConfig
from goldenverba.components.util import get_environment
import asyncio
import instructor
from langsmith import traceable
from langsmith.run_helpers import get_current_run_tree
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
import logging

load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

class AnswerResponse(BaseModel):
    """
    Model for the answer response.
    """
    answer: str = Field(..., description="The generated answer to the query")
    reasoning: str = Field(..., description="The reasoning behind the answer")

class OpenAIGenerator(Generator):
    """
    OpenAI Generator using LangSmith and Instructor.
    """

    def __init__(self):
        super().__init__()
        self.name = "OpenAI"
        self.description = "Using OpenAI LLM models with LangSmith and Instructor to generate answers to queries"
        self.context_window = 10000

        models = ["gpt-4o-mini", "gpt-4o"]

        self.config["Model"] = InputConfig(
            type="dropdown",
            value=models[0],
            description="Select an OpenAI Model",
            values=models,
        )

        if os.getenv("OPENAI_API_KEY") is None:
            self.config["API Key"] = InputConfig(
                type="password",
                value="",
                description="You can set your OpenAI API Key here or set it as environment variable `OPENAI_API_KEY`",
                values=[],
            )
        if os.getenv("OPENAI_BASE_URL") is None:
            self.config["URL"] = InputConfig(
                type="text",
                value="https://api.openai.com/v1",
                description="You can change the Base URL here if needed",
                values=[],
            )

        # Initialize OpenAI client
        self.client = None

    async def initialize_client(self, config):
        openai_key = get_environment(
            config, "API Key", "OPENAI_API_KEY", "No OpenAI API Key found"
        )
        openai_url = get_environment(
            config, "URL", "OPENAI_BASE_URL", "https://api.openai.com/v1"
        )

        async_client = AsyncOpenAI(api_key=openai_key, base_url=openai_url)
        self.client = instructor.apatch(async_client)

    @traceable
    async def generate_answer(self, messages: list, model: str) -> tuple[AnswerResponse, str]:
        # Log the model being used for answer generation
        logger.info(f"Generating answer with model: {model}")

        # Create the chat completion request
        response = await self.client.chat.completions.create(
            model=model,
            response_model=AnswerResponse,
            max_retries=2,
            messages=messages,
        )

        # Retrieve the current run details
        run = get_current_run_tree()
        run_id = run.id if run else "unknown"

        # Log the generated answer and associated run_id
        logger.info(f"Answer generated, run_id: {run_id}")
        
        # Return the response and the run_id
        return response, run_id

    async def generate_stream(
        self,
        config: dict,
        query: str,
        context: str,
        conversation: list[dict] = [],
    ):
        if not self.client:
            await self.initialize_client(config)

        system_message = config.get("System Message").value
        model = config.get("Model", {"value": "gpt-4o-mini"}).value

        messages = self.prepare_messages(query, context, conversation, system_message)

        try:
            logger.info(f"Generating stream response for query: {query[:50]}...")
            response, run_id = await self.generate_answer(messages, model)
            logger.info(f"Stream response generated, run_id: {run_id}")
            yield {"message": response.answer, "finish_reason": None, "runId": run_id}
            yield {"message": f"\n\nReasoning: {response.reasoning}", "finish_reason": "stop", "runId": run_id}
        except Exception as e:
            logger.error(f"Error generating stream response: {str(e)}")
            yield {"message": f"Error: {str(e)}", "finish_reason": "error", "runId": ""}

    def prepare_messages(
        self, query: str, context: str, conversation: list[dict], system_message: str
    ) -> list[dict]:
        messages = [
            {
                "role": "system",
                "content": system_message,
            }
        ]

        for message in conversation:
            messages.append({"role": message.type, "content": message.content})

        messages.append(
            {
                "role": "user",
                "content": f"Answer this query: '{query}' with this provided context: {context}",
            }
        )

        return messages