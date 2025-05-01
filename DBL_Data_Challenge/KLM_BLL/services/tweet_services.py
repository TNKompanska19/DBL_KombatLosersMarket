import json
import datetime
from KLM_BLL.models.tweet_model import Tweet
from KLM_DAL.repositories.tweet_repository import TweetRepository
from KLM_DAL.mappers.tweet_mapper import TweetMapper

class TweetExtractor:
    def __init__(self, json_file_path, connection):
        self.json_file_path = json_file_path
        self.tweet_repository = TweetRepository(connection)

    def convert_to_sql_datetime(self, date_str):
        if not date_str:
            return None
        try:
            return datetime.datetime.strptime(date_str, "%a %b %d %H:%M:%S +0000 %Y")
        except (ValueError, TypeError):
            return None

    def extract_data_from_json(self):
        with open(self.json_file_path, 'r', encoding='utf-8') as f:
            json_objects = f.readlines()

        for line in json_objects:
            try:
                tweet = json.loads(line)
                user = tweet.get("user", {})
                if not user.get("id"):
                    continue

                # Create the Business Layer Tweet Model
                business_tweet = Tweet(
                    tweet_id=tweet.get('id'),
                    created_at=self.convert_to_sql_datetime(tweet.get('created_at')),
                    text=tweet.get('text'),
                    source=tweet.get('source'),
                    user_id=user.get('id'),
                    lang=tweet.get('lang'),
                    tweet_url=f"https://twitter.com/{user.get('screen_name')}/status/{tweet.get('id')}",
                    is_quote_status=tweet.get('is_quote_status', False),
                    truncated=tweet.get('truncated', False),
                    quote_count=tweet.get('quote_count', 0),
                    reply_count=tweet.get('reply_count', 0),
                    retweet_count=tweet.get('retweet_count', 0),
                    favorite_count=tweet.get('favorite_count', 0),
                    in_reply_to_status_id=tweet.get('in_reply_to_status_id'),
                    in_reply_to_user_id=tweet.get('in_reply_to_user_id')
                )

                # Convert to Data Layer Model
                tweet_data = TweetMapper.to_data_model(business_tweet)

                # Insert into the database
                self.tweet_repository.insert_or_update_tweet(tweet_data)

            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")
