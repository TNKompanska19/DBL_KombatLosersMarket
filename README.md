<h1 align="center">DBL Data Challenge</h1>
<p align = "center">
   <img src = "https://img.shields.io/github/languages/count/TNKompanska19/DBL_KombatLosersMarket?style=for-the-badge">
   <img src = "https://img.shields.io/github/repo-size/TNKompanska19/DBL_KombatLosersMarket?style=for-the-badge">
   <img src = "https://img.shields.io/github/last-commit/TNKompanska19/DBL_KombatLosersMarket?style=for-the-badge">
   <img src = "https://img.shields.io/github/languages/top/TNKompanska19/DBL_KombatLosersMarket?style=for-the-badge">
</p>
<h2 align="center"><i>KombatLosersMarket Participants</i></h2>
  <table align="center">
  <tr>
    <th><i>Ádám Bakos</i></th>
  </tr>
  <tr>
    <th><i>Teodora Kompanska</i></th>
  </tr>
  <tr>
    <th><i>Gergely Bruncsák</i></th>
  </tr>
  <tr>
    <th><i>Levente Tatar</i></th>
  </tr> 
  <tr>
    <th><i>Hyelynn Choi</i></th>
  </tr> 
   <tr>
    <th><i>Pavel Kotorov</i></th>
  </tr> 
</table>
 <h2>📌 Project Overview</h2> 
 <p> This project explores how airlines engage with customers on Twitter. As part of the DBL Data Challenge, our focus is on <strong>KLM Royal Dutch Airlines</strong>. We analyzed tweet sentiment, responsiveness, and engagement, aiming to deliver actionable insights to improve KLM's social media strategy. </p> 
 <h2>🎯 Objective</h2> 
 <p> Analyze and compare how airlines use Twitter for brand communication and customer interaction, with a special focus on KLM. We assess sentiment, engagement, responsiveness, and public perception. </p>
 <h2>🏁 Client Goals</h2> 
 <ul> 
   <li>Assess how well KLM’s tweets are received by the public</li> 
   <li>Benchmark KLM against competitors in terms of engagement & sentiment</li> 
   <li>Evaluate Twitter’s role as a support and branding tool</li> <li>Recommend improvements for boosting customer satisfaction</li> 
 </ul> 
 <h2>📊 Dataset Summary</h2> 
 <ul> 
   <li><strong>Total Tweets:</strong> ~6.5 million</li> 
   <li><strong>Airlines Covered:</strong> 13 major airlines</li>
   <li><strong>Time Range:</strong> May 22, 2019 – March 30, 2020</li>
   <li><strong>File Size:</strong> 35.2 GB (JSON format)</li>
 </ul> 
 <h2>🛠️ Key Tasks Completed</h2> 
 <ol> 
   <li><strong>Data Cleaning:</strong> Filtered and retained relevant tweet attributes</li>
   <li><strong>Conversation Definition:</strong> Defined tweet reply chains as conversations</li>
   <li><strong>Sentiment Analysis:</strong> Applied TabularisAI to classify tweets (5 sentiment levels)</li> 
   <li><strong>EDA:</strong> Explored trends in volume, sentiment, and engagement</li> 
   <li><strong>Benchmarking:</strong> Compared KLM's performance with other airlines</li> 
   <li><strong>Reporting:</strong> Visualized findings and suggested strategic improvements</li> 
 </ol> 
 <h2>🧰 Tools & Technologies</h2> 
 <ul> 
   <li><strong>PostgreSQL:</strong> Efficient storage and querying of tweet data</li> 
   <li><strong>Python:</strong> Data processing, analysis, and automation</li>
   <li><strong>TabularisAI:</strong> Pre-trained sentiment analysis model</li> 
   <li><strong>Jupyter Notebook:</strong> EDA, visualizations, and documentation</li>
   <li><strong>Git:</strong> Version control and team collaboration</li> </ul>  </p>

<h2>⚙️ Installation & Setup Guide</h2>
<details> <summary><strong>🗄️ PostgreSQL Installation</strong></summary> 
  <h4>📍 On Windows/macOS:</h4> 
  <ol> 
    <li>Download and install from: <a href="https://www.postgresql.org/download/">https://www.postgresql.org/download/</a></li> 
    <li>Set a password for the <code>postgres</code> user during setup.</li> <li>Create a new database (e.g., <code>dbl_challenge</code>).</li> 
    <li>Use <code>pgAdmin</code> to run and manage queries.</li> 
  </ol> 
  <h4>🐧 On Linux:</h4> 
  <pre><code>sudo apt update sudo apt install postgresql postgresql-contrib sudo -u postgres createdb airline_tweets </code></pre> </details> 
  <details> <summary><strong>📦 Downloading the Project</strong></summary> 
    <h4>📂 Option 1: Clone via Git</h4> 
    <pre><code>git clone https://github.com/TNKompanska19/DBL_KombatLosersMarket</code></pre> 
    <h4>📁 Option 2: Download as ZIP</h4> <ol> <li>Visit <a href="https://github.com/TNKompanska19/DBL_KombatLosersMarket">GitHub Repository</a></li> 
      <li>Click the green <code>Code</code> button → <code>Download ZIP</code></li> <li>Extract the ZIP to your preferred location</li> 
    </ol> 
    <p>👉 After downloading, choose one of the subprojects to proceed: <code>Loading_Database/</code> or <code>DBL_Challenge/</code></p> 
  </details> 
  <details> <summary><strong>🏗️ Project Structure & Python Setup</strong></summary>
    <h3>📁 <code>1. Loading_Database/</code> – Build a Local Database</h3> 
    <p>Use this if you want to:</p> 
    <ul> 
      <li>Load and explore the full dataset locally</li>
      <li>Customize or run your own SQL queries</li> </ul> 
    <h4>🧰 Key Contents</h4> 
    <ul> 
      <li>JSON Loader Scripts</li> 
      <li>Schema Definitions</li> 
      <li>Conversation Miner</li> 
      <li>Sentiment Annotator</li> 
    </ul> 
    <h4>📚 Required Libraries</h4> 
    <pre><code>pip install pandas numpy seaborn matplotlib psycopg2 sqlalchemy plotly networkx scikit-learn transformers datasets scipy</code></pre> 
    <h4>⚙️ Configuration</h4> <p>Edit <code>configuration.py</code> with your environment details:</p> 
    <ul> 
      <li><code>DB_ADMIN_URL</code> – PostgreSQL admin connection string</li> 
      <li><code>NEW_DB_NAME</code> – Name of the new database</li> 
      <li><code>FOLDER</code> – Folder path for raw JSON</li> 
      <li><code>DATABASE_URL</code> – Main DB connection string</li> 
    </ul> 
    <pre><code>Format: postgresql://username:password@localhost:5432/database_name</code></pre> 
    <h4>🚀 Run</h4> <pre><code>cd Loading_Database/ python main.py </code></pre> <hr> 
    <h3>📁 <code>2. DBL_Challenge/</code> – Use Shared Database/ Or the one you created vie Loading_Database\main.py</h3> 
    <p>Use this if you want to:</p> 
    <ul> 
      <li>Generate plots and statistics from our presentations</li>
      <li>Skip creating a local DB</li> 
      <li>Connect to our hosted PostgreSQL DB</li>
      <li>Use the database that you created</li>
    </ul> 
    <h4>📦 Contents</h4> 
    <ul> 
      <li>Jupyter notebooks</li> 
      <li>SQL scripts</li> 
      <li>Visualization modules</li> 
    </ul> 
    <p>📚 Instructions & Structure:</p> <ul> 
      <li>conversations_tree_storage (presentation_3)</li>
        <ul>
        <li>Create_graph_file_for_conversations.py -> run this to create a graph storage file for conversations (used in some sentiment analysis related plots )</li>
        </ul>
      <li>map (presentation_3)</li>
        <ul>
        <li>sentiment_map_advanced.py -> run this to generate a world map with sentiment traffic (adjustable for a given month in the script itself)</li>
        </ul>
      <li>presentation_1</li>
        <ul>
        <li>presentation_1_EDA.ipynb -> run all from start to regenerate plots and statistics used in presentation 1</li>
        </ul>
      <li>presentation_2</li>
        <ul>
        <li>KLM_rlvnt_languages.ipynb -> run to derive basic statistic about different languages that appear in KLM related tweets for the whole database</li>
        <li> length_vis_distr.ipynb -> run to derive visualization about lenght distribution of conversations</li>
        <li> Senti_Models_evaluation.ipynb -> run to derive heatmaps and statistic that evaluate sentiment model performance on a manually premade dataset (availabe under testing_datasets)</li>
        <li> sentiment_analysis_viz.ipynb -> run to derive exploratory visualization about sentiment analysis on single tweets.</li>
        </ul>
      <li>sentiment_analysis (presentation_3)</li>
        <ul>
        <li>avg_senti.ipynb -> run to derive bar plot for average sentiment score per ailine</li>
        <li>Reply_delay_vs_Av_senti_score.ipynb -> run to derive scatter plot with linear regression line that investigates correlation between ailine reply speed and sentimen of a conversation.</li>
        <li>Sentiment_Evolution_violin_heatmap.ipynb -> run to derive violin plots and heatmaps that inverstigate sentimen evoltion of conversations and airline reply tone, and performance during different times of the day of different airline (resp.) </li>
        <li>Sentiment_Time_Visualization.ipynb -> run to derive descriptive plot for change in conversations sentiment over a given timespan.</li>
        <li>Visualization.ipynb -> run to derive descriptive heatmaps that investigates customer sentiment based on the language of the posts.</li>
        </ul> 
    </ul> </details>


<hr> <p align="center"> <em>Made with ❤️ by the DBL Data Challenge Team</em>
