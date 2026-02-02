import json
import re
from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_groq.chat_models import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, field_validator, ValidationError
from warnings import filterwarnings
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Get API key
groq_api_key = os.getenv("GROQ_API_KEY")


filterwarnings("ignore")


class MediaAlertAnalysis(BaseModel):
    """Media Alert Analysis Model."""
    
    summarization: str = Field(description="Concise, factual summary of the media alert")
    sentiment: str = Field(description="Alert sentiment")
    flag: str = Field(description="Classification level")

    @field_validator("summarization")
    def validate_summarization(cls, v):
        if not v or len(v) < 10:
            raise ValueError("Summarization must be at least 10 characters long.")
        return v

    @field_validator("sentiment")
    def validate_sentiment(cls, v):
        valid_values = {"Positive", "Negative", "Neutral"}
        v = v.capitalize()
        if v not in valid_values:
            raise ValueError(f"Sentiment must be one of {valid_values}.")
        return v

    @field_validator("flag")
    def validate_flag(cls, v):
        valid_values = {"High", "Medium", "Low"}
        v = v.capitalize()
        if v not in valid_values:
            raise ValueError(f"Flag must be one of {valid_values}.")
        return v


class AramcoMediaAlertRAG:
    """This defines an AramcoMediaAlertRAG class, which represents a system for analyzing media alerts. The class has the following attributes:
    
    classification_data: a dictionary containing classification data (more on this later)
    llm: a ChatGroq object, which is a Groq AI model used for natural language processing
    prompt_template: a PromptTemplate object, which defines a detailed prompt with strict guidelines for analyzing media alerts
    output_parser: a PydanticOutputParser object, which parses the output of the analysis into a MediaAlertAnalysis format"""
    
    def __init__(self, classification_data: Dict[str, Any]):
        self.classification_data = classification_data
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant", 
            temperature=0.1,
            groq_api_key=groq_api_key
        )
        
        # Detailed prompt with strict guidelines
        self.prompt_template = PromptTemplate(
        template="""Strictly analyze the media alert using Aramco's classification criteria:

Classification Levels: {classification_levels}

Media Alert: {media_alert}

Analysis Guidelines:
1. Summarize key points objectively
2. Determine precise sentiment
3. Classify alert level rigorously
4. Avoid speculation
5. Focus on verifiable information

{format_instructions}""",
            input_variables=["classification_levels", "media_alert"],
            partial_variables={
                "format_instructions": PydanticOutputParser(pydantic_object=MediaAlertAnalysis).get_format_instructions()
            }
        )
        
        self.output_parser = PydanticOutputParser(pydantic_object=MediaAlertAnalysis)

    def _preprocess_alert(self, media_alert: str) -> str:
        # Clean and standardize input
        media_alert = re.sub(r'\s+', ' ', media_alert).strip()
        return media_alert

    def process_media_alert(self, media_alert: str) -> Dict[str, Any]:
        """
        Process the media alert with proactive rate limit handling for Groq API.
        - Waits if remaining requests/tokens are low, based on response headers.
        - Handles 429 errors with retry-after as fallback.
        """
        import time
        import requests
        cleaned_alert = self._preprocess_alert(media_alert)
        chain = self.prompt_template | self.llm | self.output_parser
        max_retries = 5
        attempt = 0
        min_remaining_requests = 2  # proactively wait if only 2 requests left
        min_remaining_tokens = 500  # proactively wait if only 500 tokens left
        while attempt < max_retries:
            try:
                result = chain.invoke({
                    "classification_levels": json.dumps(self.classification_data["Classification Levels"], indent=2),
                    "media_alert": cleaned_alert
                })
                # Try to get response headers from the LLM object if available
                response_headers = None
                if hasattr(self.llm, 'last_response') and hasattr(self.llm.last_response, 'headers'):
                    response_headers = self.llm.last_response.headers
                # If not, try to get from result (if chain returns it)
                if hasattr(result, 'headers'):
                    response_headers = result.headers
                # Proactive rate limit handling
                if response_headers:
                    try:
                        remaining_requests = int(response_headers.get('x-ratelimit-remaining-requests', 100))
                        remaining_tokens = int(response_headers.get('x-ratelimit-remaining-tokens', 10000))
                        reset_requests = response_headers.get('x-ratelimit-reset-requests')
                        reset_tokens = response_headers.get('x-ratelimit-reset-tokens')
                        # If close to request or token limit, wait for reset
                        if remaining_requests <= min_remaining_requests and reset_requests:
                            # Parse reset_requests (e.g., '2m59.56s' or '7.66s')
                            wait_sec = self._parse_reset_time(reset_requests)
                            print(f"Approaching request rate limit. Waiting {wait_sec} seconds for reset...")
                            time.sleep(wait_sec)
                        elif remaining_tokens <= min_remaining_tokens and reset_tokens:
                            wait_sec = self._parse_reset_time(reset_tokens)
                            print(f"Approaching token rate limit. Waiting {wait_sec} seconds for reset...")
                            time.sleep(wait_sec)
                    except Exception:
                        pass
                return result.dict()
            except Exception as e:
                # Check for HTTP 429 Too Many Requests
                if hasattr(e, 'response') and e.response is not None and hasattr(e.response, 'status_code') and e.response.status_code == 429:
                    retry_after = 2  # default seconds
                    if 'retry-after' in e.response.headers:
                        try:
                            retry_after = float(e.response.headers['retry-after'])
                        except Exception:
                            pass
                    print(f"Rate limit hit. Retrying after {retry_after} seconds...")
                    time.sleep(retry_after)
                    attempt += 1
                    continue
                # Optionally, handle other rate limit headers for logging
                if hasattr(e, 'response') and e.response is not None and hasattr(e.response, 'headers'):
                    headers = e.response.headers
                    print(f"Rate limit info: requests left: {headers.get('x-ratelimit-remaining-requests')}, tokens left: {headers.get('x-ratelimit-remaining-tokens')}")
                raise e
        raise Exception("Exceeded maximum retries due to rate limiting.")

    def _parse_reset_time(self, reset_str):
        """
        Parse reset time from header string (e.g., '2m59.56s', '7.66s') to seconds (float).
        """
        import re
        if not reset_str:
            return 2.0
        # Match patterns like '2m59.56s' or '7.66s'
        m = re.match(r"(?:(\d+)m)?([\d.]+)s", reset_str)
        if m:
            minutes = int(m.group(1)) if m.group(1) else 0
            seconds = float(m.group(2))
            return minutes * 60 + seconds
        try:
            return float(reset_str)
        except Exception:
            return 2.0




class clasification_level():
    def __init__(self) -> None:
        self.classification_data = {
  "Classification Levels": {
    "High": {
      "Criteria for Flagging": [
        "News articles or social media posts focused on Aramco with the potential to impact reputation, operations, or regulatory standing if not managed proactively. These alerts need close monitoring to avoid escalation."
      ],
      "Examples of Media Alerts and Emerging Issues": [
        "Coordinated social media campaigns directly targeting Aramco's policies or practices",

        "Community protests or worker strikes involving Aramco operations, provided there are no immediate safety risks.",
        "Early media coverage of regulatory changes expected to impact Aramco's compliance costs",
        "Negative analyst reports or warnings of credit downgrades specifically referencing Aramco.","Criticism from major stakeholders, such as investors or NGOs, directly addressing Aramco's activities or decisions",

        "Scandals mentioning Aramco and involving its affiliates or partners with potential indirect reputational impact on the company."
      ],
      "Action Required": [
        {
          "Action": "Action Required"
        }
      ]
    },
    "Medium": {
      "Criteria for Flagging": [
        "News articles or social media posts referencing Aramco, with limited reach or potential impact but may evolve over time. Requires monitoring to detect trends early."
      ],
      "Examples of Media Alerts and Emerging Issues": [
        "Negative social media chatter directly about Aramco’s sustainability issues or ESG initiatives",
        "Niche publications covering minor operational inefficiencies specifically related to Aramco.",
        "Low-reach accounts posting speculative rumors directly involving Aramco, its people, or its operations",
        "Regional policy changes explicitly mentioning Aramco with potential delayed impacts on the company",
        "Anonymous employee reviews raising minor grievances specifically about working at Aramco."
      ],
      "Action Required": [
        {
          "Action": "Assess"
        }
      ]
    },
    "Low": {
      "Criteria for Flagging": [
        "Important mentions in news articles or social media posts with minimal impact on operations or reputation but with potential strategic significance for tracking trends, opportunities, or achievements. These alerts are logged for reference, trend analysis, or future action."
      ],
      "Examples of Media Alerts and Emerging Issues": [
        "Coverage of Aramco’s press releases or announcements containing inaccurate, speculative, or misleading content",
        "Mentions of Aramco’s participation in major industry conferences or events in top-tier media",
        "Major industry news or early signs of an industry-wide issue specifically referencing Aramco or its role",
        "Major crises affecting a competitor with implications or comparisons drawn to Aramco",
        "Mentions of Aramco’s major partnerships or collaborations featured in top-tier media"
      ],
      "Action Required": [
        {
          "Action": "No Action Needed"
        }
      ]
    }
  }
}



def process_rag(translated_text, url, title):
    """Process media alert using RAG."""
    try:
        if not isinstance(translated_text,str):
            raise ValueError("Translated text must be a string.")

        # print(f"Translated text: {translated_text}")
        classification = clasification_level()
        data = classification.classification_data
        # print(f"Classification data: {data}")
        rag_system = AramcoMediaAlertRAG(data)
        # print(f"RAG system: {rag_system}")

        # Process the alert
        result = rag_system.process_media_alert(translated_text)
        # print(f"RAG result: {result}")

        # Extract classification details
        classification_details = data["Classification Levels"].get(result["flag"], {})
        
        formatted_result = {
    "Alert Analysis": {
        "Summary": result["summarization"],
        "Overall Sentiment": result["sentiment"],
        "Alert Level": result["flag"],
        "URL": url,
        "Title": title,
        "Classification Details": {
            "Criteria": classification_details.get("Criteria for Flagging", []),
            "Required Action": classification_details.get("Action Required", [{"Action": "No specific action defined"}])[0]["Action"]
        }
    }
}

# Ensure proper JSON encoding before sending to Telegram
        # message_text = json.dumps(formatted_result, indent=2, ensure_ascii=False)

        
        # return json.dumps(formatted_result, indent=2, ensure_ascii=False)
        return formatted_result
    except ValueError as ve:
        print(f"Value Error: {str(ve)}")
        return str(ve)
    except Exception as e:
        print(f"RAG processing error: {str(e)}")
        return str(e)
    