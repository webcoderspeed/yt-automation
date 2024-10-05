import os
import random
import schedule
import time
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Scopes for the YouTube Data API
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def authenticate_youtube():
    """
    Authenticates the user and returns the YouTube API client.
    """
    creds = None
    token_path = 'token.json'  # Path to store the user's access and refresh tokens

    # Check if the token already exists (reusing tokens)
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # If no valid credentials, prompt the user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("./client-secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())

    youtube = build('youtube', 'v3', credentials=creds)
    return youtube

def upload_video_to_youtube(youtube, video_path, title, description, tags=None):
    """
    Uploads a video to YouTube.
    
    Args:
        youtube (Resource): The authenticated YouTube API client.
        video_path (str): The path to the video file to upload.
        title (str): The title of the video.
        description (str): The description of the video.
        tags (list): Optional list of tags for the video.
    """
    print(f"Uploading video: {video_path}")

    # Media upload object for the video file
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

    # Metadata for the video
    request_body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags or [],
            'categoryId': '20',  # Gaming category (you can change based on your content)
        },
        'status': {
            'privacyStatus': 'public'  # 'public', 'private', or 'unlisted'
        }
    }

    # Insert the video
    upload_request = youtube.videos().insert(
        part='snippet,status',
        body=request_body,
        media_body=media
    )

    response = upload_request.execute()
    print(f"Video uploaded successfully: {response['id']}")

def get_videos_to_post(download_folder, count=5):
    """
    Reads the videos from the latest folder and selects up to `count` videos to post.
    
    Args:
        download_folder (str): Path to the folder containing downloaded videos.
        count (int): The number of videos to select for posting.

    Returns:
        list: A list of file paths to videos.
    """
    video_files = [os.path.join(download_folder, f) for f in os.listdir(download_folder) if f.endswith('.mp4')]
    
    if len(video_files) >= count:
        return random.sample(video_files, count)
    return video_files

def schedule_video_posting(video_paths):
    """
    Schedules the posting of 5 videos at different times.
    
    Args:
        video_paths (list): List of video file paths to post.
    """
   # Schedule posting at different times using filename as title and description
    for i in range(5):
        file_path = video_paths[i]
        title = os.path.basename(file_path).rsplit('.', 1)[0]  # Get the filename without extension
        description = title  # Use the filename as the description

        # Define the scheduled time based on index
        if i == 0:
            schedule_time = "03:00"
        elif i == 1:
            schedule_time = "09:00"
        elif i == 2:
            schedule_time = "13:00"
        elif i == 3:
            schedule_time = "16:00"
        elif i == 4:
            schedule_time = "23:00"

        # Schedule the video upload
        schedule.every().day.at(schedule_time).do(upload_video_to_youtube, youtube, file_path, title, description)

    print("Scheduled video posts at 3AM, 9AM, 1PM, 4PM, and 11PM using file names as titles and descriptions.")

    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    """
    Main function to load the latest videos and schedule them for posting.
    """
    today_date = datetime.now().strftime("%Y-%m-%d")
    download_folder = f"./downloads/{today_date}"

    if not os.path.exists(download_folder):
        print(f"No download folder found for today: {download_folder}")
        return

    videos_to_post = get_videos_to_post(download_folder)
    schedule_video_posting(videos_to_post)

if __name__ == "__main__":
    main()
