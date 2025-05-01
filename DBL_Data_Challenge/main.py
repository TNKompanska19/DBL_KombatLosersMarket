import os
from KLM_DAL.database_conn import conn  # Database connection
from KLM_BLL.services.tweet_services import TweetExtractor
from KLM_BLL.services.user_services import UserExtractor
# Path to the JSON file (ensure you have a valid JSON file for testing)
json_file_path = "airlines-1558546003827.json"

extractor = UserExtractor(json_file_path, conn)
# Initialize the TweetExtractor
tweet_extractor = TweetExtractor(json_file_path, conn)

# Execute the data extraction
extractor.extract_data_from_json()
tweet_extractor.extract_data_from_json()

print("Extraction and insertion completed.")
