import sys
import os
import pandas as pd
import serpapi
from dotenv import load_dotenv

load_dotenv()

def google_dork(query, api_key, max_results=200, strict_terms=None):
    client = serpapi.Client(api_key=api_key)
    data = []
    start = 0
    while True:
        params = {
            "engine": "google",
            "q": query,
            "num": 100,
            "start": start
        }
        result = client.search(params)
        organic = result.get("organic_results", [])
        if not organic:
            break
        for item in organic:
            link = item.get("link", "")
            snippet = item.get("snippet", "")
            content = (link + " " + snippet).lower()
            if strict_terms:
                if all(term.lower() in content for term in strict_terms):
                    data.append({"Link": link, "Description": snippet})
            else:
                data.append({"Link": link, "Description": snippet})
        start += 100
        if len(data) >= max_results:
            break
    return data

def save_results(folder, filename, data):
    df = pd.DataFrame(data)
    filepath = os.path.join(folder, filename)
    df.to_excel(filepath, index=False)
    print(f"Saved {len(data)} results to {filename}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 PyInsTalker.py @username \"Person Name\"")
        sys.exit(1)

    username = sys.argv[1]
    name = sys.argv[2]
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        print("SERPAPI_KEY not found in .env file.")
        sys.exit(1)

    folder_name = username.replace("@", "") + "_" + name.replace(" ", "_")
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    print(f"Searching for {name} and {username} combination")
    general_query = f"{name} {username}"
    general_results = google_dork(general_query, api_key)
    if general_results:
        save_results(folder_name, f"general_{folder_name}.xlsx", general_results)
    else:
        print("No results found for general search")

    print(f"Searching for {username} only")
    at_query = username
    at_results = google_dork(at_query, api_key)
    if at_results:
        save_results(folder_name, f"at_only_{folder_name}.xlsx", at_results)
    else:
        print("No results found for @username search")

    print(f"Searching for \"{name}\" only")
    name_query = f"\"{name}\""
    name_results = google_dork(name_query, api_key)
    if name_results:
        save_results(folder_name, f"name_only_{folder_name}.xlsx", name_results)
    else:
        print("No results found for \"name\" search")

    social_sites = {
        "instagram": "site:instagram.com",
        "twitter": "site:twitter.com",
        "tiktok": "site:tiktok.com",
        "facebook": "site:facebook.com",
        "youtube": "site:youtube.com"
    }

    for site, dork in social_sites.items():
        print(f"Searching on {site} with \"{name}\" and \"{username}\"")
        query_full = f"{dork} \"{name}\" \"{username}\""
        strict_terms = [name.lower(), username.lower()]
        if "site:" in dork:
            strict_terms.append(dork.split(":")[1].lower())
        results_full = google_dork(query_full, api_key, strict_terms=strict_terms)
        if results_full:
            filename_full = f"{site}_name_and_username_{folder_name}.xlsx"
            save_results(folder_name, filename_full, results_full)
        else:
            print(f"No results found on {site} for \"{name}\" and \"{username}\"")

        print(f"Searching on {site} with \"{name}\" only")
        query_name_only = f"{dork} \"{name}\""
        strict_terms_name = [name.lower()]
        if "site:" in dork:
            strict_terms_name.append(dork.split(":")[1].lower())
        results_name_only = google_dork(query_name_only, api_key, strict_terms=strict_terms_name)
        if results_name_only:
            filename_name_only = f"{site}_name_only_{folder_name}.xlsx"
            save_results(folder_name, filename_name_only, results_name_only)
        else:
            print(f"No results found on {site} for \"{name}\" only")
