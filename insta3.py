import instaloader
import os
from datetime import timedelta, datetime

# Function to format timestamp in IST
def timestamped_filename(post):
    # Convert UTC time to IST
    ist_offset = timedelta(hours=5, minutes=30)
    ist_time = post.date_utc + ist_offset
    return ist_time.strftime('%Y-%m-%d_%H-%M-%S')

# Create an instance of Instaloader
L = instaloader.Instaloader(
    download_pictures=True,
    download_videos=True,
    download_video_thumbnails=False,
    download_geotags=False,
    download_comments=False,
    save_metadata=False,
    compress_json=False,
    post_metadata_txt_pattern=' ',
    storyitem_metadata_txt_pattern=' ',
    filename_pattern="{date_utc}_UTC"
)

# Prompt user for credentials
IG_USERNAME = input("Enter your Instagram username: ")
IG_PASSWORD = input("Enter your Instagram password: ")

# Path to the session file 
SESSION_FILE = f"session-{IG_USERNAME}.instaloader"

#  Try to load session or login
if IG_USERNAME and IG_PASSWORD:
    try:
        if os.path.exists(SESSION_FILE):
            L.load_session_from_file(IG_USERNAME, SESSION_FILE)
            print("Session Loaded.")
        else:
            L.context.log("Login...")
            L.login(IG_USERNAME, IG_PASSWORD)
            L.save_session_to_file(SESSION_FILE)
            print("Login successful and session saved.")
    except Exception as e:
        print(f"Failed to log in or load session: {e}")
        exit()

# Function to download profile content
def download_profile_content(profile_name):
    #Get the profile 
    try:
        profile = instaloader.Profile.from_username(L.context, profile_name)
        print(f"Profile '{profile_name}' retrieved.")
    except Exception as e:
        print(f"Failed to retrieve profile: {e}")
        return
    
    # Download profile id
    try:
        L.save_profile_id(profile)
        print("Profile id saved.")
    except Exception as e:
        print(f"Failed to save profile id: {e}")
    
    # Create a directory for the profile
    if not os.path.exists(profile_name):
        os.makedirs(profile_name)
        print(f"Directory '{profile_name}' created.")

    # Download profile picture
    try:
        L.download_profilepic(profile)
        print("Profile picture downloaded.")
    except Exception as e:
        print(f"Failed to download profile picture: {e}")
    
    # Download posts
    try:
        for post in profile.get_posts():
            L.download_post(post, target=profile_name)
        print("Posts downloaded.")
    except Exception as e:
        print(f"Failed to download posts: {e}")

    # Download tagged posts
    try:
        for post in profile.get_tagged_posts():
            L.download_post(post, target=f"{profile_name}/tagged")
        print("Tag Posts downloaded.")
    except Exception as e:
        print(f"Failed to download tagged posts: {e}")

    # Download stories
    try:
        for story in L.get_stories(userids=[profile.userid]):
            for item in story.get_items():
                L.download_storyitem(item, profile_name + '/stories')
        print("Stories downloaded.")
    except Exception as e:
        print(f"Failed to download stories: {e}")

    # Download highlights
    try:
        for highlight in L.get_highlights(profile):
            for item in highlight.get_items():
                try:
                    L.download_storyitem(item, os.path.join(profile_name, "highlights", highlight.title))
                except instaloader.exceptions.InstaloaderException as ex:
                    if "HTTP error 410" in str(ex):
                        print("skipping highlight due to 410 error")
                        continue
                    else:
                        raise ex
            print(f"Highlight '{highlight.title}' downloaded.")
        print("Highlights downloaded.")
    except Exception as e:
        print(f"Failed to download Highlights: {e}")

    # Download IGTV videos
    try:
        for igtv in profile.get_igtv_posts():
            L.download_post(igtv, target=profile_name + '/igtv')
        print("IGTV videos downloaded.")
    except Exception as e:
        print(f"Failed to download IGTV videos: {e}")

    print(f"Downloaded all content from {profile_name}")
    
# Main loop to download multiple profiles
while True:
    PROFILE_NAME = input("Enter the profile username to download content from (or 'done' to finish): ")
    if PROFILE_NAME == 'done':
        break
    download_profile_content(PROFILE_NAME)

print("Process complete.")