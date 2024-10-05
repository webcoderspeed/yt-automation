import os
import random
from datetime import datetime
import schedule
import time
from googleapiclient.discovery import build
import yt_dlp

API_KEY = 'YOUTUBE_APIKEY'  # Replace with your YouTube API Key

# List of keywords for random selection
keywords = [
    "gaming shorts", "epic gameplay", "best gaming highlights", "daily game clips",
    "pro gamer tips", "glitch tricks", "gaming tutorials", "top gaming moments",
    "gaming strategies", "funny gaming fails", "fastest game wins", "trend`ing game glitches",
    "mobile gaming clips", "console gameplay", "multiplayer game highlights"
]

# List of region codes for US and European countries
region_codes = ['US', 'GB', 'DE', 'FR', 'IT', 'ES', 'NL', 'SE', 'PL', 'BE']

def search_youtube_shorts(max_results=5):
    """
    Searches for YouTube Shorts related to gaming using random keywords and regions.

    Args:
        max_results (int): The maximum number of results to return.

    Returns:
        list: A list of video URLs and video titles.
    """
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    # Randomly select a keyword and a region
    query = random.choice(keywords)
    region_code = random.choice(region_codes)

    print(f"Searching with query: '{query}' in region: {region_code}")

    # Search for YouTube Shorts ordered by date (latest first)
    search_response = youtube.search().list(
        q=query,
        part='id,snippet',
        maxResults=max_results,
        order='date',  # Order by upload date
        type='video',
        regionCode=region_code  # Filter by region
    ).execute()

    video_info = []
    for item in search_response['items']:
        video_id = item['id']['videoId']
        video_title = item['snippet']['title']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        video_info.append({'url': video_url, 'title': video_title})

    return video_info

def is_video_downloaded(video_title, download_path):
    """
    Checks if a video has already been downloaded based on its title.

    Args:
        video_title (str): The title of the YouTube video.
        download_path (str): The path where the videos are saved.

    Returns:
        bool: True if the video is already downloaded, False otherwise.
    """
    video_files = os.listdir(download_path)
    # Normalize file names by removing special characters from the video title
    sanitized_title = video_title.replace("/", "_").replace("\\", "_")
    
    # Check if any file in the folder starts with the sanitized title (ignores file extension)
    for file_name in video_files:
        if file_name.startswith(sanitized_title):
            return True
    return False

def download_video(video_info, download_path):
    """
    Downloads a single YouTube video if it hasn't already been downloaded.

    Args:
        video_info (dict): Dictionary containing video URL and title.
        download_path (str): Path to save the downloaded video.
    """
    video_url = video_info['url']
    video_title = video_info['title']
    sanitized_title = video_title.replace("/", "_").replace("\\", "_")  # Sanitize title for file system
    file_path = os.path.join(download_path, f"{sanitized_title}.mp4")

    if is_video_downloaded(sanitized_title, download_path):
        print(f"Skipping {video_title}: already downloaded.")
        return False

    ydl_opts = {
        'outtmpl': os.path.join(download_path, f'{sanitized_title}.%(ext)s'),  # Save with sanitized title as filename
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading: {video_url}")
            ydl.download([video_url])
            print(f"Downloaded video: {video_title}")
            return True
    except Exception as e:
        print(f"Failed to download video {video_title}. Error: {e}")
        return False

def count_downloaded_videos(download_path):
    """
    Counts the number of videos in the download directory.

    Args:
        download_path (str): The path where the videos are saved.

    Returns:
        int: Number of video files in the directory.
    """
    return len([f for f in os.listdir(download_path) if f.endswith('.mp4')])

def ensure_five_videos(download_path):
    """
    Ensures that there are 5 videos in the download directory. If fewer than 5 are downloaded,
    the function searches and downloads more until the folder contains 5 videos.
    """
    max_results = 5
    
    while count_downloaded_videos(download_path) < 5:
        print("Checking if 5 videos are downloaded...")
        video_info_list = search_youtube_shorts(max_results)
        
        for video_info in video_info_list:
            if count_downloaded_videos(download_path) >= 5:
                break
            download_video(video_info, download_path)
        
        print(f"Current downloaded videos: {count_downloaded_videos(download_path)}")

def download_daily_shorts():
    """
    Downloads the latest YouTube Shorts for the day and stores them in a date-specific folder.
    Ensures that 5 videos are downloaded.
    """
    # Create a folder named with the current date (YYYY-MM-DD)
    today_date = datetime.now().strftime("%Y-%m-%d")
    download_path = f"./downloads/{today_date}"
    
    os.makedirs(download_path, exist_ok=True)

    # Ensure the folder contains exactly 5 videos
    ensure_five_videos(download_path)

def schedule_daily_download():
    """
    Schedule the download of YouTube Shorts every day at 12 AM.
    """
    schedule.every().day.at("00:00").do(download_daily_shorts)
    
    print("Scheduled daily downloads at 12 AM. Waiting...")

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    schedule_daily_download()
