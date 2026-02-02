from langchain_groq.chat_models import ChatGroq
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Optional



load_dotenv()
 
# Define the model
llm = ChatGroq(
    model="llama-3.1-8b-instant",  # Example Groq model, change as needed
)


class Joke(BaseModel):
    '''Joke to tell user.'''

    setup: str = Field(description="The setup of the joke")
    punchline: str = Field(description="The punchline to the joke")
    rating: Optional[int] = Field(description="How funny the joke is, from 1 to 10")

structured_model = llm.with_structured_output(Joke)
data =structured_model.invoke("Tell me a joke about cats")
print(data)