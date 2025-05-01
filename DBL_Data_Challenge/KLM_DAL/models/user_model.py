class UserData:
    def __init__(self, user_id, name, screen_name, location, url, description,
                 profile_image_url, profile_banner_url, followers_count, friends_count,
                 listed_count, favourites_count, statuses_count, verified, protected, created_at):
        self.user_id = user_id
        self.name = name
        self.screen_name = screen_name
        self.location = location
        self.url = url
        self.description = description
        self.profile_image_url = profile_image_url
        self.profile_banner_url = profile_banner_url
        self.followers_count = followers_count
        self.friends_count = friends_count
        self.listed_count = listed_count
        self.favourites_count = favourites_count
        self.statuses_count = statuses_count
        self.verified = verified
        self.protected = protected
        self.created_at = created_at
