# main.py
import subprocess
import os

# DB creation script in the same folder as main.py
db_script = "create_database.py"

# Other import scripts inside data_loading folder
scripts = [
    "import_tweet.py",
    "import_users.py",
    "import_hashtags.py",
    "import_tweet_hashtags.py",
    "import_user_mentions.py",
    "import_symbols.py",
    "import_places.py"
]

# Folder containing your data loading scripts
script_folder = os.path.join(os.getcwd(), "data_loading")

# Run DB creation script first (current directory)
print(f"Running: {db_script}")
subprocess.run(["python", db_script], check=True)

# Then run each script inside data_loading
for script in scripts:
    full_path = os.path.join(script_folder, script)
    print(f"Running: {full_path}")
    subprocess.run(["python", full_path], check=True)
