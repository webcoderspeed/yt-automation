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
    if len(video_paths) < 5:
        print(f"Not enough videos to post, found {len(video_paths)} videos.")
        return

    youtube = authenticate_youtube()

    # Define video metadata (change as needed)
    titles = ["Epic Gameplay", "Gaming Highlights", "Best Game Clips", "Daily Game", "Gaming Tutorial"]
    descriptions = ["Epic moments in gaming.", "The best gaming highlights.", "Enjoy the best gameplay moments.", "Daily game highlights.", "Pro gamer tips and tricks."]
    
    # Schedule posting at different times
    schedule.every().day.at("03:00").do(upload_video_to_youtube, youtube, video_paths[0], titles[0], descriptions[0])
    schedule.every().day.at("09:00").do(upload_video_to_youtube, youtube, video_paths[1], titles[1], descriptions[1])
    schedule.every().day.at("13:00").do(upload_video_to_youtube, youtube, video_paths[2], titles[2], descriptions[2])
    schedule.every().day.at("16:00").do(upload_video_to_youtube, youtube, video_paths[3], titles[3], descriptions[3])
    schedule.every().day.at("23:00").do(upload_video_to_youtube, youtube, video_paths[4], titles[4], descriptions[4])

    print("Scheduled video posts at 3AM, 9AM, 1PM, 4PM, and 11PM.")

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
