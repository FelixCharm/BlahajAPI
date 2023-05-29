import praw
import requests
import os
import time
import colorama
import datetime
import random
import string
import mysql.connector
import hashlib

mysql = mysql.connector.connect(
    host='localhost',
    user='root',
    password=os.environ['mysql_password'],
    database='blahaj'
)

FILE_NAME_LEN = 6 # 2,176,782,336 possible characters

client_id = os.environ['reddit_client_id']
client_secret = os.environ['reddit_client_secret']
user_agent = "Blahaj/1.0"
subreddit_name = "blahaj"
download_loc = "images-temp"
move_loc = "images"

post_limit = 75

# Logo credit to https://github.com/GeopJr/BLAHAJ/blob/main/data/ascii.txt :3

logo = """
\033[38;5;117m                                          ,(((/                                 
\033[38;5;117m                                        /(((((                                  
\033[38;5;117m                                       ((((#((                              (// 
\033[38;5;117m                                      (((((((.                           *(((/  
\033[38;5;219m                                    /(######/                          *((((/   
\033[38;5;219m                                 *//%#####((/                         ((#((/    
\033[38;5;219m               ,*/********/////////////////(//*           (%*      ,((##((      
\033[38;5;255m      ,*/((///(//////////((/(///////(/////(////*,(*#((/(/((//////###(###(/(     
\033[38;5;255m   /(((((((//((///((////((((((/(((((((((((((((((/(((##((#%(##(/((///*(&#(##/    
\033[38;5;255m  /#((%(#(((((//#((((((((((((((((((((((((#(((((((((((/##(((((//((//*    ####(/  
\033[38;5;219m   (((###(###(#(#####(###############((#((((((((/((//(((#/(/////            ,,  
\033[38;5;219m     ,(###%####%&%#############(#(#(####(((((((/(((/////*//,                    
\033[38;5;219m         . .....*#(#######(((###(#(##(##(((/(/(/////,                           
\033[38;5;117m          .. ....,..........,..*#%#######/(                                     
\033[38;5;117m               ..  .............,*%%%%#%((((/                                   
\033[38;5;117m                       **,,,****//*(##((###(#(((                                
\033[38;5;117m                                        &#(#/#((((((((#      \033[39m
"""

reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent,
                     ratelimit_seconds=600)

def create_table_if_not_exists():
    cursor = mysql.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INT PRIMARY KEY AUTO_INCREMENT,
            url VARCHAR(255) NOT NULL,
            title VARCHAR(255) NOT NULL,
            author VARCHAR(255) DEFAULT 'N/A',
            description TEXT
        )
    """)
    mysql.commit()

def md5sum(filename):
    with open(filename, 'rb', buffering=0) as f:
        return hashlib.file_digest(f, 'md5').hexdigest()

def get_file_hashes():
    hashes = []
    for files in os.walk('images'):
        for file in files[2]:
            hashes.append(md5sum('images/' + file))        
    return hashes

def random_string(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def log(line):
    print(f"\033[38;5;240m[\033[38;5;117mS\033[38;5;219mh\033[38;5;255ma\033[38;5;219mr\033[38;5;117mk\033[38;5;240m] \033[38;5;240m[\033[38;5;135m{datetime.datetime.now().strftime('%H:%M:%S')}\033[38;5;240m] \033[38;5;171m{line}\033[39m")

def get_posts():
    posts = []
    subreddit = reddit.subreddit(subreddit_name)

    # Get the top posts from the subreddit
    # log("Getting top posts from \033[38;5;219mr/blahaj\033[38;5;117m...")
    # top_posts = subreddit.top(limit=post_limit)
    # posts += top_posts
    # log("Top posts retrieved\033[38;5;117m!")

    # Get the latest posts from the subreddit
    log("Getting latest posts from \033[38;5;219mr/blahaj\033[38;5;117m...")
    latest_posts = subreddit.new(limit=post_limit)
    posts += latest_posts
    log("Latest posts retrieved\033[38;5;117m!")

    # Get the hot posts from the subreddit
    # log("Getting hot posts from \033[38;5;219mr/blahaj\033[38;5;117m...")
    # hot_posts = subreddit.hot(limit=post_limit)
    # posts += hot_posts
    # log("Hot posts retrieved\033[38;5;117m!")

    return posts

def download_and_save(hashes):
    did_download = False
    posts = get_posts()
    for post in posts:
        if post.is_self or not post.url.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            continue

        # reset_time = int(reddit.auth.limits['reset_timestamp'])
        # current_time = time.time()
        # delay = reset_time - current_time
        # if delay > 0:
        #     log(f"Sleeping for \033[38;5;117m{delay}\033[38;5;171m seconds due to rate limit")
        #     time.sleep(delay)

        try:
            image_url = post.url
            image_filename = os.path.basename(image_url)
            author = "u/"+post.author.name
            title = post.title

            image_path = os.path.join(download_loc, image_filename)

            response = requests.get(image_url)
            response.raise_for_status()

            with open(image_path, 'wb') as f:
                f.write(response.content)

            file_hash = md5sum(image_path)
            if file_hash not in hashes:
                # print(f"Moving image `{image_path}` ({file_hash}) to images...")
                new_file_name = random_string(FILE_NAME_LEN)
                while os.path.isfile(f"images/{new_file_name}.png"):
                    new_file_name = random_string(FILE_NAME_LEN)
                os.rename(image_path, 'images/' + new_file_name + '.png')
                hashes.append(file_hash)

                description = f"\"{title}\" ({image_url})"

                add_to_database(new_file_name, author, description)
                log(f"Downloaded: {image_url} ({new_file_name})")
                hashes.append(file_hash)
                if not did_download:
                    did_download = True
            else:
                # print(f"Image `{image_path}` ({file_hash}) already exists, removing from temp directory...")
                os.remove(image_path)
            
        except Exception as e:
            print(e)

    return did_download

def add_to_database(file_name, author, description):

    url = f"https://blahaj.transgirl.dev/images/{file_name}"

    cursor = mysql.cursor()
    cursor.execute(f"INSERT INTO images (url, title, author, description) VALUES (%s, %s, %s, %s)", (url, file_name, author, description))
    mysql.commit()
    cursor.close()

def main():

    # Create a directory to save the images
    if not os.path.exists(download_loc):
        os.makedirs(download_loc)

    if not os.path.exists(move_loc):
        os.makedirs(move_loc)

    os.system('cls' if os.name == 'nt' else 'clear')
    colorama.init()
    print(logo)
    log("Starting \033[38;5;219mSharkScrape\033[38;5;117m...")
    hashes = get_file_hashes()
    while True:
        if download_and_save(hashes):
            log("All images downloaded successfully\033[38;5;117m!")
        time.sleep(10)


if __name__ == "__main__":
    create_table_if_not_exists()
    main()