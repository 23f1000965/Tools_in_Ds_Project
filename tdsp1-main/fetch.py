import requests
import pandas as pd
import time
import logging
from typing import List, Dict

class GitHubScraper:
    def __init__(self, token: str):
        """
        Initialize the GitHub scraper with your API token.
        
        Args:
            token (str): GitHub Personal Access Token
        """
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _make_request(self, url: str, params: dict = None) -> Dict:
        """
        Make a request to the GitHub API with rate limit handling.
        """
        while True:
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                sleep_time = max(reset_time - time.time(), 0) + 1
                self.logger.warning(f"Rate limit hit. Sleeping for {sleep_time} seconds")
                time.sleep(sleep_time)
            else:
                self.logger.error(f"Error {response.status_code}: {response.text}")
                response.raise_for_status()

    def clean_company_name(self, company: str) -> str:
        """
        Clean up company names according to specifications.
        """
        if not company:
            return ""
        
        # Strip whitespace and @ symbol, convert to uppercase
        cleaned = company.strip().lstrip('@').upper()
        return cleaned

    def search_users(self, location: str, min_followers: int) -> List[Dict]:
        """
        Search for GitHub users in a specific location with minimum followers.
        """
        users = []
        page = 1
        
        while True:
            self.logger.info(f"Fetching users page {page}")
            
            query = f"location:{location} followers:>={min_followers}"
            params = {
                'q': query,
                'per_page': 100,
                'page': page
            }
            
            url = f"{self.base_url}/search/users"
            response = self._make_request(url, params)
            
            if not response.get('items'):
                break
                
            for user in response['items']:
                user_data = self._make_request(user['url'])
                
                # Extract only the required fields with exact matching names
                cleaned_data = {
                    'login': user_data['login'],
                    'name': user_data['name'] if user_data['name'] else "",
                    'company': self.clean_company_name(user_data.get('company')),
                    'location': user_data['location'] if user_data['location'] else "",
                    'email': user_data['email'] if user_data['email'] else "",
                    'hireable': str(user_data['hireable']).lower() if user_data['hireable'] is not None else "",
                    'bio': user_data['bio'] if user_data['bio'] else "",
                    'public_repos': user_data['public_repos'],
                    'followers': user_data['followers'],
                    'following': user_data['following'],
                    'created_at': user_data['created_at']
                }
                
                users.append(cleaned_data)
                
            page += 1
            
        return users
    
    def get_user_repositories(self, username: str, max_repos: int = 500) -> List[Dict]:
        """
        Get repositories for a specific user.
        """
        repos = []
        page = 1
        
        while len(repos) < max_repos:
            self.logger.info(f"Fetching repositories for {username}, page {page}")
            
            params = {
                'sort': 'pushed',
                'direction': 'desc',
                'per_page': 100,
                'page': page
            }
            
            url = f"{self.base_url}/users/{username}/repos"
            response = self._make_request(url, params)
            
            if not response:
                break
                
            for repo in response:
                # Extract only the required fields with exact matching names
                repo_data = {
                    'login': username,  # Adding owner's login as required
                    'full_name': repo['full_name'],
                    'created_at': repo['created_at'],
                    'stargazers_count': repo['stargazers_count'],
                    'watchers_count': repo['watchers_count'],
                    'language': repo['language'] if repo['language'] else "",
                    'has_projects': str(repo['has_projects']).lower(),
                    'has_wiki': str(repo['has_wiki']).lower(),
                    'license_name': repo['license']['key'] if repo.get('license') else ""
                }
                repos.append(repo_data)
                
            if len(response) < 100:
                break
                
            page += 1
            
        return repos[:max_repos]

def main():
    # Get GitHub token
    token = input("Enter your GitHub token: ").strip()
    if not token:
        print("Token is required. Exiting...")
        return

    # Initialize scraper
    scraper = GitHubScraper(token)
    
    # Search for users in Bangalore with >100 followers
    users = scraper.search_users(location='Bangalore', min_followers=100)
    
    # Save users to CSV
    users_df = pd.DataFrame(users)
    users_df.to_csv('users.csv', index=False)
    
    # Get repositories for each user
    all_repos = []
    for user in users:
        repos = scraper.get_user_repositories(user['login'])
        all_repos.extend(repos)
    
    # Save repositories to CSV
    repos_df = pd.DataFrame(all_repos)
    repos_df.to_csv('repositories.csv', index=False)
    print(f"Scraped {len(users)} users and {len(all_repos)} repositories")
    
    # Create README.md
    with open('README.md', 'w') as f:
        f.write(f"""# GitHub Users in Bangalore

GitHub User & Repository Scraper
This project uses the GitHub API to scrape information about users and their repositories, focusing on active developers in Bangalore with at least 100 followers.

    Data was collected from the GitHub API for users in Bangalore with over 100 followers.
    Analyzing the data revealed the varied company affiliations of users across tech sectors.
    Recommendation: Developers should optimize their profiles for visibility, especially in high-tech cities like Bangalore.
🚀 Features
    Fetches GitHub users based on location and follower count.
    Collects metadata about users and their repositories.
    Handles GitHub API rate limits gracefully.
    Saves data into CSV files.
Files
    users.csv: Contains information about 602 GitHub users in Bangalore with over 100 followers
    repositories.csv: Contains information about 50215 public repositories from these users
    fetch.py: Python script used to collect this data
Data Collection
    Data collected using GitHub API
    Date of collection: 2024-10-28
    Only included users with 100+ followers
    Up to 500 most recently pushed repositories per user
🧠 Skills Demonstrated
    Python scripting and automation
    REST API integration and pagination
    Data cleaning and structuring with pandas
    Rate limit management
    Markdown and file handling
📌 How to Use
    Clone the repository
    Run fetch.py
    Enter your GitHub token when prompted
    Get users.csv, repositories.csv, and this README!


if __name__ == "__main__":
    main()
