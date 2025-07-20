import os
from dotenv import load_dotenv
from agents import AsyncOpenAI, OpenAIChatCompletionsModel, Agent, Runner
import asyncio
import chainlit as cl


# Scenario 1

load_dotenv()

@cl.on_chat_start
async def setup():

    MODEL_NAME = "gemini-2.0-flash"
    API_KEY = os.getenv("GEMINI_API_KEY")

    external_client = AsyncOpenAI(
        api_key = API_KEY,
        base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    model = OpenAIChatCompletionsModel(
        openai_client = external_client,
        model = MODEL_NAME
    )

    cl.user_session.set("chat_history", [])
    
    restaurant_agent = Agent(
        name = "Restaurant Finder",
        instructions = (
            "You are a restaurant assistant. Based on the user's prompt, recommend popular, highly rated restaurants"
            "Include cuisine, location, and pricing info if available. Be coincise and helpful"
        ),
        model = model
    )

    cl.user_session.set("agent", restaurant_agent)

    await cl.Message(content="Welcome! I can help you find restaurants based on your cravings. Just tell me what you're looking for!").send()



# Scenario 2

@cl.on_message
async def main(message: cl.Message):
    
    msg = await cl.Message(content="Thinking or Processing...").send()

    Restaurant = cl.user_session.get("agent")
    
    history = cl.user_session.get("chat_history")

    history.append({"role": "user", "content": message.content})


    result = await Runner.run(starting_agent = Restaurant , input = history)

    msg.content = result.final_output
    await msg.update()


    cl.user_session.set("chat_history", result.to_input_list())


    


if __name__ == "__main__":
    asyncio.run(main())




