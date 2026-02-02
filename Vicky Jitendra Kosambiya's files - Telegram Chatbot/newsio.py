import os
import json
from datetime import datetime
from newsdataapi import NewsDataApiClient
from dotenv import load_dotenv

load_dotenv()

def fetch_news(query="aramco"):
    """Fetch news articles based on a query and save them in a timestamped JSON file."""
    
    api_key = os.getenv("NEWSIO_API")
    if not api_key:
        raise ValueError("API key not found. Check your .env file.")
    
    api = NewsDataApiClient(apikey=api_key)
    response = api.news_api(q=query)

    # Ensure response contains data
    if "results" not in response or not response["results"]:
        print("No news articles found.")
        return None

    # Generate a timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"news_{timestamp}.json"

    # Save the response to a JSON file
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(response, file, indent=4, ensure_ascii=False)

    # print(f"News data saved to {filename}")
    return response  # Return filename for reference

# Example usage
# if __name__ == "__main__":
#     fetch_news()
