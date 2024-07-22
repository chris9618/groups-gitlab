import requests
import pandas as pd

# Constants
GITLAB_API_URL = "https://gitlab.com/api/v4"
# Replace with your personal access token
ACCESS_TOKEN = "token"
# Replace with the ID of the root group you want to start with
ROOT_GROUP_ID = "12345"

# Function to get subgroups of a given group
def get_subgroups(group_id, page=1):
    url = f"{GITLAB_API_URL}/groups/{group_id}/subgroups"
    headers = {"PRIVATE-TOKEN": ACCESS_TOKEN}
    params = {
        "per_page": PER_PAGE,
        "page": page
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json(), response.headers

# Recursive function to get all nested subgroups
def get_all_subgroups(group_id, parent_info=[], level=0, count=0):
    all_subgroups = []
    page = 1
    while True:
        subgroups, headers = get_subgroups(group_id, page)
        for subgroup in subgroups:
            current_info = parent_info + [subgroup["name"]]
            subgroup_details = {
                "Level": level,
                **{f"Level {i} Group Name": name for i, name in enumerate(current_info)},
                "Hierarchical Path": " / ".join(current_info)
            }
            all_subgroups.append(subgroup_details)
            count += 1
            nested_subgroups, nested_count = get_all_subgroups(subgroup["id"], current_info, level + 1, count)
            all_subgroups.extend(nested_subgroups)
            count = nested_count
        if 'X-Next-Page' in headers and headers['X-Next-Page']:
            page = int(headers['X-Next-Page'])
        else:
            break
    return all_subgroups, count

# Main script execution
if __name__ == "__main__":
    # Fetch the root group details
    root_group_response = requests.get(f"{GITLAB_API_URL}/groups/{ROOT_GROUP_ID}", headers={"PRIVATE-TOKEN": ACCESS_TOKEN})
    root_group_response.raise_for_status()
    root_group = root_group_response.json()
    root_group_name = root_group['name']
    
    all_subgroups, total_count = get_all_subgroups(ROOT_GROUP_ID, [root_group_name], 0)

    # Convert list of dictionaries to DataFrame
    df = pd.DataFrame(all_subgroups)

    # Fill missing columns to avoid KeyError in DataFrame creation
    max_level = df["Level"].max()
    for level in range(max_level + 1):
        df[f"Level {level} Group Name"] = df.get(f"Level {level} Group Name", "")

    # Drop the Level column as it's no longer needed
    df = df.drop(columns=["Level"])

    # Display all rows and full column content
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_colwidth', None)

    # Print DataFrame
    print(df)

    # Save the DataFrame to an Excel file
    df.to_excel("subgroups_details.xlsx", index=False)

    # Print total count of subgroups
    print(f"Total number of subgroups: {total_count}")
