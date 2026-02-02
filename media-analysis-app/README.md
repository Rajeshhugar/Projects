# README.md

# Media Analysis App

## Overview

The Media Analysis App is a Streamlit-based application that allows users to input video files, video URLs, and news article URLs. The app integrates various functionalities for audio conversion, transcription, translation, and news article scraping, providing a comprehensive tool for media analysis.

## Features

- Upload video files or provide video URLs for analysis.
- Fetch and process news articles from provided URLs.
- Convert video to audio and transcribe audio files into text.
- Translate transcribed text into different languages.
- Analyze and summarize news articles.

## Project Structure

```
media-analysis-app
├── src
│   ├── core
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── config.py
│   │   └── constants.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── audio_service.py
│   │   ├── news_service.py
│   │   ├── transcription_service.py
│   │   ├── translation_service.py
│   │   └── video_service.py
│   ├── utils
│   │   ├── __init__.py
│   │   ├── audio_converter.py
│   │   ├── file_handler.py
│   │   ├── transcriber.py
│   │   └── video_downloader.py
│   ├── models
│   │   ├── __init__.py
│   │   └── alert.py
│   └── scrapers
│       ├── __init__.py
│       └── news_scrapers.py
├── tests
│   ├── __init__.py
│   └── test_services
│       └── __init__.py
├── .env.example
├── requirements.txt
├── setup.py
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/media-analysis-app.git
   cd media-analysis-app
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables by copying `.env.example` to `.env` and filling in the required values.

## Usage

To run the application, execute the following command:
```
streamlit run src/core/app.py
```

Open your web browser and navigate to `http://localhost:8501` to access the app.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.