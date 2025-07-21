import os
import sys
import pandas as pd

def find_excel_files(base_dirs):
    files = []
    for base_dir in base_dirs:
        for root, _, filenames in os.walk(base_dir):
            for filename in filenames:
                if filename.endswith('.xlsx'):
                    files.append(os.path.join(root, filename))
    return files

def normalize_columns(df):
    df.columns = [col.strip().lower() for col in df.columns]
    return df

def extract_matching_rows(file_path, terms):
    df = pd.read_excel(file_path)
    df = normalize_columns(df)

    if 'link' in df.columns and 'description' in df.columns:
        mask = df.apply(lambda row: all(
            term.lower() in (str(row['link']).lower() + " " + str(row['description']).lower())
            for term in terms
        ), axis=1)
        return df[mask][['link', 'description']]
    else:
        return pd.DataFrame(columns=['link', 'description'])

def main():
    if len(sys.argv) < 2:
        print("Usage: python PyFilter.py <\"term1\"> [\"term2\"] [\"term3\"] ...")
        sys.exit(1)

    terms = sys.argv[1:]
    base_dirs = ["crislessamakeup_Cris_Bringmann", "crislessamakeup_Cristiane_Bringmann"]

    all_matches = []

    files = find_excel_files(base_dirs)

    for file in files:
        matches = extract_matching_rows(file, terms)
        if not matches.empty:
            all_matches.append(matches)

    if all_matches:
        result = pd.concat(all_matches, ignore_index=True)
        result.drop_duplicates(subset=['link'], inplace=True)
        result.to_excel("filtered_links.xlsx", index=False)
        print(f"Saved {len(result)} unique matching links to filtered_links.xlsx")
    else:
        print("No matching links found.")

if __name__ == "__main__":
    main()
