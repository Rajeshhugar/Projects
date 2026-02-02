import os
import tempfile
import requests
import logging
import urllib.parse
import bs4
import re
from pathlib import Path
import streamlit as st

class VideoDownloader:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def validate_url(self, url):
        """Validate if the URL is properly formatted"""
        try:
            parsed_url = urllib.parse.urlparse(url)
            if parsed_url.scheme in ['http', 'https'] and parsed_url.netloc:
                return True
            self.logger.warning(f"Invalid URL attempted: {url}")
            return False
        except Exception as e:
            self.logger.error(f"URL validation exception: {str(e)}")
            return False

    def download_twitter_video(self, url):
        """Download video from Twitter URL"""
        try:
            api_url = f"https://twitsave.com/info?url={url}"
            response = requests.get(api_url)
            data = bs4.BeautifulSoup(response.text, "html.parser")
            
            # Find download buttons
            download_button = data.find_all("div", class_="origin-top-right")
            if not download_button:
                st.error("No video found in the tweet.")
                return None
                
            quality_buttons = download_button[0].find_all("a")
            if not quality_buttons:
                st.error("No video download links found.")
                return None
                
            highest_quality_url = quality_buttons[0].get("href")
            
            # Download the video
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                response = requests.get(highest_quality_url, stream=True)
                total_size = int(response.headers.get("content-length", 0))
                
                # Create a progress bar
                progress_bar = st.progress(0)
                progress_text = st.empty()
                
                downloaded_size = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)
                        downloaded_size += len(chunk)
                        # Update progress
                        if total_size:
                            progress = downloaded_size / total_size
                            progress_bar.progress(progress)
                            progress_text.text(f"Downloaded: {downloaded_size // 1024 // 1024}MB / {total_size // 1024 // 1024}MB")
                
                progress_text.text("Download completed!")
                return temp_file.name
                
        except Exception as e:
            st.error(f"Error downloading Twitter video: {str(e)}")
            self.logger.error(f"Twitter download error: {str(e)}")
            return None

    def download_regular_video(self, url):
        """Download video from a direct video URL"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                response = requests.get(url, stream=True, timeout=30)
                if response.status_code != 200:
                    st.error(f"Download failed. Status code: {response.status_code}")
                    return None

                total_size = int(response.headers.get("content-length", 0))
                
                # Create a progress bar
                progress_bar = st.progress(0)
                progress_text = st.empty()
                
                downloaded_size = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)
                        downloaded_size += len(chunk)
                        # Update progress
                        if total_size:
                            progress = downloaded_size / total_size
                            progress_bar.progress(progress)
                            progress_text.text(f"Downloaded: {downloaded_size // 1024 // 1024}MB / {total_size // 1024 // 1024}MB")
                
                progress_text.text("Download completed!")
                return temp_file.name

        except requests.exceptions.RequestException as e:
            st.error(f"Network error during download: {str(e)}")
            self.logger.error(f"Video download error: {str(e)}")
            return None

    def download(self, url):
        """Main download method that handles both Twitter and regular video URLs"""
        if not self.validate_url(url):
            st.error("Invalid URL. Please provide a valid HTTP or HTTPS URL.")
            return None

        try:
            # Check if it's a Twitter URL
            if 'twitter.com' in url or 'x.com' in url:
                video_path = self.download_twitter_video(url)
                if video_path:
                    st.success("Video downloaded successfully from Twitter!")
                    return video_path
            elif 'aws.com' in url or 's3.amazonaws.com' in url:
                video_path = self.download_regular_video(url)
                if video_path:
                    st.success("Video downloaded successfully from AWS!")
                    return video_path
            else:
                st.text(f"Enter valid url path. Either twitter or aws s3 url")
                return None

        except Exception as e:
            st.error(f"An error occurred during download: {str(e)}")
            self.logger.error(f"Download error: {str(e)}")
            return None
        
    def video_processor(self, video_path):
        try:
            video_url = self.download(video_path)
            return video_url
        except Exception as e:
            st.error(f"An error occurred during download: {str(e)}")
            return None

# if __name__ == "__main__":
#     video_path = "https://x.com/SBA_sport/status/1863333797938262190"
#     video_downloader = VideoDownloader()
#     video_downloader.video_processor(video_path)
#     print("Video downloaded successfully!")
#     print(video_path)