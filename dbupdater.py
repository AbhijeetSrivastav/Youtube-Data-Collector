class MongoUpdater:
    def __init__(self):
        try:
            import pymongo
        except ImportError:
            raise ImportError

        # Establishing connection to client
        self.client = pymongo.MongoClient(
            "mongodb+srv://ghostalterdcarbon:SaUPOGkvpywfEAr6@cluster0.3kmmf99.mongodb.net/?retryWrites=true&w=majority")

        # Creating database
        self.database = self.client['videoinfo']

        # Creating collection
        self.collection = self.database['videodata']

    def generateJson(self, title: str, video_url: str, view: str, thumbnail_url: str, like: str, comments: list,
                     commentors: list, commented_ons: list) -> dict:
        """Generates JSON for each video"""
        return {
            'title': title,
            'video_url': video_url,
            'thumbnail_url': thumbnail_url,
            'like': like,
            'view': view,
            'comment_data': [comments, commentors, commented_ons]
        }
