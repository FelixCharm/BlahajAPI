from flask import Flask, jsonify, send_file, current_app
import mysql.connector
import random
import os

app = Flask(__name__)
mysql = mysql.connector.connect(
    host='localhost',
    user='root',
    password=os.environ['mysql_password'],
    database='blahaj'
)


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

@app.route('/')
def hello_world():
    return current_app.send_static_file('index.html')

@app.route('/images/<filename>')
def serve_image(filename):
    try:
        image_path = f'images/{filename}.png'
        return send_file(image_path, mimetype='image/png')
    except:
        return jsonify({'message': 'No such image.'}), 404

@app.route('/images/random')
def get_random_image():
    cursor = mysql.cursor(dictionary=True)
    cursor.execute('SELECT COUNT(*) FROM images')
    count = cursor.fetchone()['COUNT(*)']
    if count > 0:
        cursor.execute('SELECT * FROM images WHERE id=%s LIMIT 1', [random.randint(1, int(count))])
        image = cursor.fetchone()
        image_data = {
            'id': image['id'],
            'url': image['url'],
            'title': image['title'],
            'author': image['author'],
            'description': image['description']
        }
        return jsonify(image_data)
    else:
        return jsonify({'message': 'No images available.'}), 404


if __name__ == '__main__':
    create_table_if_not_exists()
    app.run()
