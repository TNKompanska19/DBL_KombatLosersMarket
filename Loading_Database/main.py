# main.py
import subprocess
import os, sys

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# DB creation script in the same folder as main.py
db_script = os.path.join(os.path.dirname(__file__), "create_database.py")

# Other import scripts inside data_loading folder
data_loading_scripts = [
    "import_tweet.py",
    "import_users.py",
    "import_hashtags.py",
    "import_tweet_hashtags.py",
    "import_user_mentions.py",
    "import_symbols.py",
    "import_places.py",
    "insert_full_text.py",
    "created_at_timestamp.py",
]

# Scripts in conversations/database folder
conversation_scripts = [
    "conversation_table_insert.py",
    "deleting_single_tweet_conv.py",
    "change_conversations_ids.py"
]

sentiment_scripts = [
    "row_enumeration_tweets.py",
    "import_sentiment.py",
]

additional_conv_scripts = [
    "additional_columns.py",
    "conversation_senti_score_until_position.py",
]

# Folder paths
base_dir = os.path.dirname(__file__)

data_loading_folder = os.path.join(base_dir, "data_loading")
conversation_folder = os.path.join(base_dir, "conversations", "database")
sentiment_folder = os.path.join(base_dir, "sentiment_analysis")

# Run DB creation script first
print(f"Running: {db_script}")
subprocess.run([sys.executable, db_script], check=True, cwd=base_dir)

# Run scripts in data_loading
for script in data_loading_scripts:
    full_path = os.path.join(data_loading_folder, script)
    print(f"Running: {full_path}")
    subprocess.run([sys.executable, full_path], check=True, cwd=base_dir)

# Run scripts in conversations/database
for script in conversation_scripts:
    full_path = os.path.join(conversation_folder, script)
    print(f"Running: {full_path}")
    subprocess.run([sys.executable, full_path], check=True, cwd=base_dir)

# Run scripts in sentiment_analysis
for script in sentiment_scripts:
    full_path = os.path.join(sentiment_folder, script)
    print(f"Running: {full_path}")
    subprocess.run([sys.executable, full_path], check=True, cwd=base_dir)

# Run additional scripts in conversations/database
for script in additional_conv_scripts:
    full_path = os.path.join(conversation_folder, script)
    print(f"Running: {full_path}")
    subprocess.run([sys.executable, full_path], check=True, cwd=base_dir)