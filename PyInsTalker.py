import sys
import os
import pandas as pd
import serpapi
from dotenv import load_dotenv

load_dotenv()

def search_instagram_posts(username, api_key):
    client = serpapi.Client(api_key=api_key)
    query = f'site:instagram.com "{username}"'
    params = {
        "engine": "google",
        "q": query,
        "num": 100
    }
    result = client.search(params)

    posts = []
    for item in result.get("organic_results", []):
        link = item.get("link", "")
        snippet = item.get("snippet", "")
        if "/p/" in link or "/reel/" in link:
            posts.append({"Link": link, "Description": snippet})
    return posts

def save_results(folder, filename, data):
    df = pd.DataFrame(data)
    filepath = os.path.join(folder, filename)
    df.to_excel(filepath, index=False)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 PyInsTalker.py @username")
        sys.exit(1)

    username = sys.argv[1].replace("@", "")
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        print("SERPAPI_KEY not found in .env file.")
        sys.exit(1)

    folder_name = username
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    print(f"Searching Instagram posts for {username}...")

    results = search_instagram_posts(username, api_key)

    if results:
        filename = f"{username}_posts.xlsx"
        save_results(folder_name, filename, results)
        print(f"Saved {len(results)} posts to {filename}")
    else:
        print("No posts found or user is private.")
