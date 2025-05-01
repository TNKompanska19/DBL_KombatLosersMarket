# data_layer/mappers/user_mapper.py
from KLM_BLL.models.user_model import User  # Business Model
from KLM_DAL.models.user_model import UserData  # Data Model

class UserMapper:
    @staticmethod
    def to_data_model(business_user: User) -> UserData:
        """
        Converts a business layer User object to the data layer UserData object.
        """
        return UserData(
            user_id=business_user.user_id,
            name=business_user.name,
            screen_name=business_user.screen_name,
            location=business_user.location,
            url=business_user.url,
            description=business_user.description,
            profile_image_url=business_user.profile_image_url,
            profile_banner_url=business_user.profile_banner_url,
            followers_count=business_user.followers_count if business_user.followers_count is not None else 0,
            friends_count=business_user.friends_count if business_user.friends_count is not None else 0,
            listed_count=business_user.listed_count if business_user.listed_count is not None else 0,
            favourites_count=business_user.favourites_count if business_user.favourites_count is not None else 0,
            statuses_count=business_user.statuses_count if business_user.statuses_count is not None else 0,
            verified=business_user.verified if business_user.verified is not None else False,
            protected=business_user.protected if business_user.protected is not None else False,
            created_at=business_user.created_at
        )
