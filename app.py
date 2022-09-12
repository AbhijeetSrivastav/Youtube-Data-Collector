import scrapper
from dbupdater import MongoUpdater

if __name__ == '__main__':
    # Scrapping  data
    scp = scrapper.Scrapper('https://www.youtube.com/user/krishnaik06')
    scp.scrapMainPageData()
    scp.scrapThumbnailLink()
    scp.scrapLikes()
    scp.scrapCommentData()

    # Updating MongoDb
    mongodb = MongoUpdater()  # instance of mongodb

    since = 0
    till = 50

    for title, video_url, view, thumbnail_url, like in zip(scp.titles, scp.videos_urls, scp.views, scp.thumbnails_urls,
                                                           scp.likes):
        # json for each video
        vid_json = MongoUpdater.generateJson(mongodb, title, video_url, view, thumbnail_url, like,
                                             scp.comments[since: till], scp.commentors[since: till],
                                             scp.commented_on[since: till])

        # Add json for each video to MongoDb
        mongodb.collection.insert_one(vid_json)

        since += till
        till += till
