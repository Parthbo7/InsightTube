from googleapiclient.discovery import build

API_KEY = "AIzaSyCknV0OR4dZl0Klv9C8YYSSpkwLNJC5j9c"

youtube = build("youtube", "v3", developerKey=API_KEY)


def get_10_recent_videos(channel_name):
    """
    Returns a list of EXACTLY the 10 most recent video links of a channel
    """

    # 1. Search channel → channelId
    search_response = youtube.search().list(
        q=channel_name,
        type="channel",
        part="id",
        maxResults=1
    ).execute()

    if not search_response["items"]:
        return []

    channel_id = search_response["items"][0]["id"]["channelId"]

    # 2. Get uploads playlist
    channel_response = youtube.channels().list(
        id=channel_id,
        part="contentDetails"
    ).execute()

    uploads_playlist = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    # 3. Get latest 50 videos
    playlist_response = youtube.playlistItems().list(
        playlistId=uploads_playlist,
        part="snippet",
        maxResults=10
    ).execute()

    video_links = []

    for item in playlist_response["items"]:
        video_id = item["snippet"]["resourceId"]["videoId"]
        video_links.append(f"https://www.youtube.com/watch?v={video_id}")

    return video_links
