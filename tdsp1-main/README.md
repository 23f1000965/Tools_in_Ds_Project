# GitHub User & Repository Scraper

This project uses the GitHub API to scrape information about users and their repositories, focusing on active developers in Bangalore with at least 100 followers.

- Data was collected from the GitHub API for users in Bangalore with over 100 followers.
- Analyzing the data revealed the varied company affiliations of users across tech sectors.
- Recommendation: Developers should optimize their profiles for visibility, especially in high-tech cities like Bangalore.


## 🚀 Features

- Fetches GitHub users based on location and follower count.
- Collects metadata about users and their repositories.
- Handles GitHub API rate limits gracefully.
- Saves data into CSV files.

## Files

1. `users.csv`: Contains information about 602 GitHub users in Bangalore with over 100 followers
2. `repositories.csv`: Contains information about 50215 public repositories from these users
3. `fetch.py`: Python script used to collect this data

## Data Collection

- Data collected using GitHub API
- Date of collection: 2024-10-28
- Only included users with 100+ followers
- Up to 500 most recently pushed repositories per user


## 🧠 Skills Demonstrated

- Python scripting and automation  
- REST API integration and pagination  
- Data cleaning and structuring with pandas  
- Rate limit management  
- Markdown and file handling

## 📌 How to Use

1. Clone the repository  
2. Run `fetch.py`  
3. Enter your GitHub token when prompted  
4. Get `users.csv`, `repositories.csv`, and this README!

---


