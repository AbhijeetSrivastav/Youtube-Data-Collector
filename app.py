from flask import Flask, render_template, request
from flask_cors import cross_origin

# from pytube import YouTube
# from io import BytesIO

import scrapper
from dbupdater import MongoUpdater

app = Flask(__name__)


@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")


@app.route('/viddata', methods=['POST', 'GET'])  # route to show the scraped data
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            # channel from main page to scrap
            searchChannel = request.form['content']

            videos_data = []

            # Scrapping  data
            scp = scrapper.Scrapper(searchChannel)
            scp.scrapMainPageData()
            scp.scrapThumbnailLink()
            scp.scrapLikes()
            scp.scrapCommentData()

            # Updating MongoDb
            mongodb = MongoUpdater()  # instance of mongodb

            since = 0
            till = 50

            for title, video_url, view, thumbnail_url, like in zip(scp.titles, scp.videos_urls, scp.views,
                                                                   scp.thumbnails_urls,
                                                                   scp.likes):
                # json for each video
                vid_json = MongoUpdater.generateJson(mongodb, title, video_url, view, thumbnail_url, like,
                                                     scp.comments[since: till], scp.commentors[since: till],
                                                     scp.commented_on[since: till])

                # Add json for each video to MongoDb
                mongodb.collection.insert_one(vid_json)

                # Storing the json in list to render
                videos_data.append(vid_json)

                since += till
                till += till

            return render_template('results.html', videos_data=videos_data)
        except Exception as e:
            print('The Exception message is: ', e)

    else:
        return render_template('index.html')


# @app.route("/download", methods=["GET", "POST"])
# def download_video():
#     if request.method == "POST":
#         # buffer = BytesIO()
#         # url = YouTube(session['link'])
#         # itag = request.form.get("itag")
#         # video = url.streams.get_by_itag(itag)
#         # video.stream_to_buffer(buffer)
#         # buffer.seek(0)
#         # return send_file(buffer, as_attachment=True, download_name="Video - YT2Video.mp4", mimetype="video/mp4")
#         pass


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8001)
