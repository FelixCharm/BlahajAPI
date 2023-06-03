import random
import string
import mysql.connector
import os
import hashlib

mysql = mysql.connector.connect(
    host='localhost',
    user='root',
    password=os.environ['mysql_password'],
    database='blahaj'
)

FILE_NAME_LEN = 6 # 2,176,782,336 possible characters

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

def move_temp(hashes):
    for files in os.walk('images-temp'):
        for file in files[2]:
            file_hash = md5sum('images-temp/' + file)
            if file_hash not in hashes:
                print(f"Moving image `{file}` ({file_hash}) to images...")
                new_file_name = random_string(FILE_NAME_LEN)
                while os.path.isfile(f"images/{new_file_name}.png"):
                    new_file_name = random_string(FILE_NAME_LEN)
                os.rename('images-temp/' + file, 'images/' + new_file_name + '.png')
                hashes.append(file_hash)
                add_to_database(new_file_name)
            else:
                print(f"Image `{file}` ({file_hash}) already exists, removing from temp directory...")
                os.remove('images-temp/' + file)

def add_to_database(file_name):

    url = f"https://blahaj.transgirl.dev/images/{file_name}"

    cursor = mysql.cursor()
    cursor.execute(f"INSERT INTO images (url, title) VALUES ('{url}', '{file_name}')")
    mysql.commit()
    cursor.close()

def main():
    hashes = get_file_hashes()
    move_temp(hashes)

if __name__ == "__main__":
    main()