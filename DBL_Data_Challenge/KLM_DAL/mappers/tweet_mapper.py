# data_layer/mappers/tweet_mapper.py
from KLM_BLL.models.tweet_model import Tweet  # Business Model
from KLM_DAL.models.tweet_model import TweetData  # Data Model

class TweetMapper:
    @staticmethod
    def to_data_model(business_tweet: Tweet) -> TweetData:
        """
        Converts a business layer Tweet object to the data layer TweetData object.
        """
        return TweetData(
            tweet_id=business_tweet.tweet_id,
            created_at=business_tweet.created_at,
            text=business_tweet.text,
            source=business_tweet.source,
            truncated=business_tweet.truncated if business_tweet.truncated is not None else False,
            is_quote_status=business_tweet.is_quote_status if business_tweet.is_quote_status is not None else False,
            quote_count=business_tweet.quote_count if business_tweet.quote_count is not None else 0,
            reply_count=business_tweet.reply_count if business_tweet.reply_count is not None else 0,
            retweet_count=business_tweet.retweet_count if business_tweet.retweet_count is not None else 0,
            favorite_count=business_tweet.favorite_count if business_tweet.favorite_count is not None else 0,
            lang=business_tweet.lang,
            tweet_url=business_tweet.tweet_url,
            user_id=business_tweet.user_id,
            in_reply_to_status_id=business_tweet.in_reply_to_status_id,
            in_reply_to_user_id=business_tweet.in_reply_to_user_id
        )
