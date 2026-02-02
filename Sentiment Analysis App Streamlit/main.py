import streamlit as st
import pandas as pd
from typing import List, Literal
from pydantic import BaseModel, condecimal
#from langchain.chat_models import ChatGroq
#from langchain.output_parsers import PydanticOutputParser
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain.prompts import PromptTemplate
from langchain_groq.chat_models import ChatGroq
import os

from dotenv import load_dotenv

load_dotenv()
# ---------------------------
# Pydantic Models
# ---------------------------
class AspectSentiment(BaseModel):
    aspect: str
    sentiment: Literal["Positive", "Negative", "Neutral","NA"]

class SentimentOutput(BaseModel):
    text: str
    overall_sentiment: Literal["Positive", "Negative", "Neutral"]
    confidence: float = condecimal(ge=0.0, le=1.0)  # type: ignore
    aspects: List[AspectSentiment]

# ---------------------------
# LangChain Chain Builder
# ---------------------------
def build_chain():
    output_parser = PydanticOutputParser(pydantic_object=SentimentOutput)

    prompt = PromptTemplate(
        template="""
You are a sentiment analysis assistant.

Analyze the following text and do the following:
1. Identify the overall sentiment.
2. Estimate a confidence score between 0 and 1.
3. For each of these aspects: {aspects_list}, return the sentiment.

Respond ONLY in JSON format as:

{format_instructions}

Text: "{text}"
""",
        input_variables=["text", "aspects_list"],
        partial_variables={"format_instructions": output_parser.get_format_instructions()}
    )

#GROQ_API_KEY= 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
    llm = ChatGroq(temperature=0.0, model_name="llama-3.1-8b-instant")

    chain = prompt | llm | output_parser
    return chain

# ---------------------------
# Streamlit App
# ---------------------------
st.set_page_config(page_title="Aspect-Based Sentiment", layout="wide")
st.title("📊 Aspect-Based Sentiment Analysis (Groq + LangChain)")

uploaded_file = st.file_uploader("Upload CSV with a column named 'Text' ", type=["csv"])
aspects_input = st.text_input("Enter aspects to analyze (comma-separated)", "Taste,Whitening ,Packaging ,Sensitivity")

if uploaded_file and aspects_input:
    df = pd.read_csv(uploaded_file)
    if "Text" not in df.columns:
        st.error("CSV must contain a column named 'Text'")
        st.stop()

    df = df.head(50)
    texts = df["Text"].dropna().tolist()
    aspects = [a.strip() for a in aspects_input.split(",") if a.strip()]

    st.info(f"Analyzing {len(texts)} texts with aspects: {aspects}")
    chain = build_chain()

    all_rows = []

    with st.spinner("Analyzing with Groq API..."):
        for text in texts:
            row = {"Text": text}
            try:
                result = chain.invoke({"text": text, "aspects_list": ", ".join(aspects)})
                result_obj = result.dict()
                row["Overall Sentiment"] = result_obj["overall_sentiment"]
                row["Confidence"] = float(result_obj["confidence"])

                # Initialize all aspects as "N/A"
                for aspect in aspects:
                    row[aspect] = "N/A"

                # Fill in aspect sentiments
                for asp in result_obj["aspects"]:
                    if asp["aspect"] in aspects:
                        row[asp["aspect"]] = asp["sentiment"]

            except OutputParserException as e:
                row["Overall Sentiment"] = "Error"
                row["Confidence"] = 0.0
                for aspect in aspects:
                    row[aspect] = "Error"
            all_rows.append(row)

    result_df = pd.DataFrame(all_rows)
    st.subheader("🔍 Combined Sentiment Table")
    st.dataframe(result_df, use_container_width=True)
