# BlahajAPI

Welcome to the Blahaj API! This API allows you to fetch random images of the beloved and adorable Blahaj shark!

This page can also be found at [blahaj.transgirl.dev](https://blahaj.transgirl.dev)

## Table of Contents

- [API Endpoints](#api-endpoints)
  - [GET /images/random](#get-imagesrandom)
  - [GET /images/&lt;filename&gt;](#get-imagesfilename)
- [Usage](#usage)
- [Additional Information](#additional-information)

## API Endpoints

### GET /images/random

This endpoint fetches the data of a random image in the database.

#### Possible Responses

- The API should almost always return the HTTP status code `200 OK`. However, if there was a problem connecting to the backend database, the API will respond with the HTTP status code `404 Not Found`.

**Image Found (`HTTP status 200`)**

```json
// Image found
{"author":"N/A","description":null,"id":17,"title":"vMEkeP","url":"https://blahaj.transgirl.dev/images/vMEkeP"}
```

- Database error / Image not found (`HTTP status 404`)

```json
// No images in database
{'message': 'No images available.'}
```

### GET /images/&lt;filename&gt;

This endpoint returns the image data of the specified filename.

#### Possible Responses

- If the image exists, the API will respond with the HTTP status code `200 OK`. If the image doesn't exist, the API will respond with the HTTP status code `404 Not Found`.

**Image Found (`HTTP status 200`)**

No JSON data will be returned, only the image will be returned.

- Image not found (`HTTP status 404`)

```json
// Image doesn't exist
{'message': 'No such image.'}
```

## Usage

To use the API, send a GET request to the specific endpoint and handle the response accordingly. You can integrate the API into your applications to display random Blahaj images or retrieve specific images by filename.

For example, to fetch a random Blahaj image, you can use the following python code in your application:

```python
import requests

data = requests.get("https://blahaj.transgirl.dev/images/random").json()
url = data["url"]
image = requests.get(url)
# Handle image result
```

## Additional Information

The Blahaj API uses publicly available images that are scraped from the [r/blahaj](https://www.reddit.com/r/blahaj) subreddit. However, if you wish to have your image removed, please [Contact Me](https://transgirl.dev/contact).