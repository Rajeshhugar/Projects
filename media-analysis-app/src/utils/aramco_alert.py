import json
import re
from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_groq.chat_models import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, field_validator, ValidationError
from warnings import filterwarnings

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
        if v not in valid_values:
            raise ValueError(f"Sentiment must be one of {valid_values}.")
        return v

    @field_validator("flag")
    def validate_flag(cls, v):
        valid_values = {"URGENT", "HIGH", "MODERATE", "LOW"}
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
            model="llama-3.2-90b-vision-preview", 
            temperature=0.1,
            groq_api_key="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"
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
        # Preprocess alert
        cleaned_alert = self._preprocess_alert(media_alert)
        
        # Create processing chain
        chain = self.prompt_template | self.llm | self.output_parser
        
        # Process alert
        result = chain.invoke({
            "classification_levels": json.dumps(self.classification_data["Classification Levels"], indent=2),
            "media_alert": cleaned_alert
        })
        
        return result.dict()




class clasification_level():
    def __init__(self) -> None:
        self.classification_data = {
  "Classification Levels": {
    "URGENT": {
      "Criteria for Flagging": [
        "News articles or social media posts focused on Aramco that pose an immediate threat to operations, reputation, regulatory compliance, safety, or leadership. These alerts require urgent intervention to prevent severe consequences."],
      "Examples of Media Alerts and Emerging Issues": [
        "Breaking news directly involving Aramco's oil spills, explosions, or environmental incidents.",

"Publicized regulatory fines, penalties, or investigations specifically targeting Aramco.",

"Reports of cyberattacks or data breaches affecting Aramco’s operational or critical systems",

        "Unauthorized public statements or social media posts by Aramco employees concerning company policies",
        "Viral impersonation scams directly involving Aramco executives or misusing the company’s brand",
        "Major protests or accidents involving Aramco sites or operations that result in fatalities",
        "Leadership misconduct allegations against Aramco executives or senior management"
      ],
      "Action Required": [
        {
          "Action": "Escalate immediately to the Aramco Major Issues WhatsApp group, Burson teams, Aramco crisis teams, legal, and executive management within 15-20 minutes"
        }
      ]
    },
    "HIGH": {
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
          "Action": "Notify the Aramco Major Issues WhatsApp group and the Burson teams within 15 to 20 minutes"
        }
      ]
    },
    "MODERATE": {
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
          "Action": "Notify the Aramco Major Issues WhatsApp group and the Burson teams within 15 to 20 minutes"
        }
      ]
    },
    "LOW": {
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
          "Action": "Notify the Aramco Major Issues WhatsApp group and the Burson teams within 15 to 20 minutes"
        }
      ]
    }
  }
}



def process_rag(translated_text):
    """Process media alert using RAG."""
    try:
        if not isinstance(translated_text, str):
            raise ValueError("Translated text must be a string.")

        # print(f"Translated text: {translated_text}")
        classification = clasification_level()
        data = classification.classification_data
        rag_system = AramcoMediaAlertRAG(data)

        # Process the alert
        result = rag_system.process_media_alert(translated_text)

        # Extract classification details
        classification_details = data["Classification Levels"].get(result["flag"], {})
        
        formatted_result = {
            "Alert Analysis": {
                "Summary": result["summarization"],
                "Overall Sentiment": result["sentiment"],
                "Alert Level": result["flag"],
                "Classification Details": {
                    "Criteria": classification_details.get("Criteria for Flagging", []),
                    "Required Action": classification_details.get("Action Required", [{"Action": "No specific action defined"}])[0]["Action"]
                }
            }
        }
        
        return json.dumps(formatted_result, indent=2)
    except ValueError as ve:
        print(f"Value Error: {str(ve)}")
        return str(ve)
    except Exception as e:
        print(f"RAG processing error: {str(e)}")
        return str(e)