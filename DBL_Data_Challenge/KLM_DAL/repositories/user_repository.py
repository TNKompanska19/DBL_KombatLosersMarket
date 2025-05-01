from KLM_DAL.models.user_model import UserData

class UserRepository:
    def __init__(self, connection):
        self.conn = connection

    def insert_or_update_user(self, user: UserData):
        query = '''
            INSERT INTO users (
                user_id, name, screen_name, location, url, description,
                profile_image_url, profile_banner_url, followers_count, friends_count,
                listed_count, favourites_count, statuses_count, verified, protected, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                name = EXCLUDED.name,
                screen_name = EXCLUDED.screen_name,
                location = EXCLUDED.location,
                url = EXCLUDED.url,
                description = EXCLUDED.description,
                profile_image_url = EXCLUDED.profile_image_url,
                profile_banner_url = EXCLUDED.profile_banner_url,
                followers_count = EXCLUDED.followers_count,
                friends_count = EXCLUDED.friends_count,
                listed_count = EXCLUDED.listed_count,
                favourites_count = EXCLUDED.favourites_count,
                statuses_count = EXCLUDED.statuses_count,
                verified = EXCLUDED.verified,
                protected = EXCLUDED.protected,
                created_at = EXCLUDED.created_at
        '''
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (
                    user.user_id,
                    user.name,
                    user.screen_name,
                    user.location,
                    user.url,
                    user.description,
                    user.profile_image_url,
                    user.profile_banner_url,
                    user.followers_count,
                    user.friends_count,
                    user.listed_count,
                    user.favourites_count,
                    user.statuses_count,
                    user.verified,
                    user.protected,
                    user.created_at
                ))
            self.conn.commit()
            print(f"[User Inserted] ID: {user.user_id}, Screen Name: {user.screen_name}")
        except Exception as e:
            print(f"[User Insert] Error: {e}")
            self.conn.rollback()
