# data_layer/models/tweet.py
class TweetData:
    def __init__(self, tweet_id, created_at, text, source, truncated, is_quote_status,
                 quote_count, reply_count, retweet_count, favorite_count, lang,
                 tweet_url, user_id, in_reply_to_status_id, in_reply_to_user_id):
        self.tweet_id = tweet_id
        self.created_at = created_at
        self.text = text
        self.source = source
        self.truncated = truncated
        self.is_quote_status = is_quote_status
        self.quote_count = quote_count
        self.reply_count = reply_count
        self.retweet_count = retweet_count
        self.favorite_count = favorite_count
        self.lang = lang
        self.tweet_url = tweet_url
        self.user_id = user_id
        self.in_reply_to_status_id = in_reply_to_status_id
        self.in_reply_to_user_id = in_reply_to_user_id
