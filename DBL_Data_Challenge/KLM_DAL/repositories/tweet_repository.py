from KLM_DAL.models.tweet_model import TweetData

class TweetRepository:
    def __init__(self, connection):
        self.conn = connection

    def insert_or_update_tweet(self, tweet: TweetData):
        query = '''
            INSERT INTO tweets (
                tweet_id, created_at, text, source, truncated,
                is_quote_status, quote_count, reply_count, retweet_count,
                favorite_count, lang, tweet_url, user_id,
                in_reply_to_status_id, in_reply_to_user_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (tweet_id) DO UPDATE SET
                created_at = EXCLUDED.created_at,
                text = EXCLUDED.text,
                source = EXCLUDED.source,
                truncated = EXCLUDED.truncated,
                is_quote_status = EXCLUDED.is_quote_status,
                quote_count = EXCLUDED.quote_count,
                reply_count = EXCLUDED.reply_count,
                retweet_count = EXCLUDED.retweet_count,
                favorite_count = EXCLUDED.favorite_count,
                lang = EXCLUDED.lang,
                tweet_url = EXCLUDED.tweet_url,
                user_id = EXCLUDED.user_id,
                in_reply_to_status_id = EXCLUDED.in_reply_to_status_id,
                in_reply_to_user_id = EXCLUDED.in_reply_to_user_id
        '''
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (
                    tweet.tweet_id,
                    tweet.created_at,
                    tweet.text,
                    tweet.source,
                    tweet.truncated,
                    tweet.is_quote_status,
                    tweet.quote_count,
                    tweet.reply_count,
                    tweet.retweet_count,
                    tweet.favorite_count,
                    tweet.lang,
                    tweet.tweet_url,
                    tweet.user_id,
                    tweet.in_reply_to_status_id,
                    tweet.in_reply_to_user_id
                ))
            self.conn.commit()
            print(f"[Tweet Inserted] ID: {tweet.tweet_id}, User ID: {tweet.user_id}")
        except Exception as e:
            print(f"[Tweet Insert] Error: {e}")
            self.conn.rollback()
