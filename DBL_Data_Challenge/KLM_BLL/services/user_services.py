import json
import datetime
from KLM_BLL.models.user_model import User
from KLM_DAL.repositories.user_repository import UserRepository
from KLM_DAL.mappers.user_mapper import UserMapper


class UserExtractor:
    def __init__(self, json_file_path, connection):
        self.json_file_path = json_file_path
        self.user_repository = UserRepository(connection)

    def convert_to_sql_datetime(self, date_str):
        if not date_str:
            return None
        try:
            return datetime.datetime.strptime(date_str, "%a %b %d %H:%M:%S +0000 %Y")
        except (ValueError, TypeError):
            return None

    def safe_int(self, value):
        try:
            return int(value) if value is not None else 0
        except Exception:
            return 0

    def safe_bool(self, value):
        return bool(value) if value is not None else False

    def extract_data_from_json(self):
        with open(self.json_file_path, 'r', encoding='utf-8') as f:
            json_objects = f.readlines()

        for line in json_objects:
            try:
                tweet = json.loads(line)
                user = tweet.get("user", {})
                if not user.get("id"):
                    continue

                # Create the Business Layer User Model
                business_user = User(
                    user_id=user.get('id'),
                    name=user.get('name'),
                    screen_name=user.get('screen_name'),
                    location=user.get('location'),
                    url=user.get('url'),
                    description=user.get('description'),
                    profile_image_url=user.get('profile_image_url'),
                    profile_banner_url=user.get('profile_banner_url'),
                    followers_count=self.safe_int(user.get('followers_count')),
                    friends_count=self.safe_int(user.get('friends_count')),
                    listed_count=self.safe_int(user.get('listed_count')),
                    favourites_count=self.safe_int(user.get('favourites_count')),
                    statuses_count=self.safe_int(user.get('statuses_count')),
                    verified=self.safe_bool(user.get('verified')),
                    protected=self.safe_bool(user.get('protected')),
                    created_at=self.convert_to_sql_datetime(user.get('created_at'))
                )

                # Convert to Data Layer User Model
                user_data = UserMapper.to_data_model(business_user)

                # Insert or update in the database
                self.user_repository.insert_or_update_user(user_data)

            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")
