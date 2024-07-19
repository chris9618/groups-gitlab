import requests
import pandas as pd

# Constants
GITLAB_API_URL = "https://gitlab.com/api/v4"
# Replace with your personal access token
ACCESS_TOKEN = "token"
# Replace with the ID of the root group you want to start with
ROOT_GROUP_ID = "12345"

# Function to get subgroups of a given group
def get_subgroups(group_id):
    url = f"{GITLAB_API_URL}/groups/{group_id}/subgroups"
    headers = {"PRIVATE-TOKEN": ACCESS_TOKEN}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# Recursive function to get all nested subgroups
def get_all_subgroups(group_id, root_group_name, level=0):
    subgroups = get_subgroups(group_id)
    all_subgroups = []

    for subgroup in subgroups:
        subgroup_details = {
            "Root Group Name": root_group_name,
            "Level": level,
            f"Level {level} Group Name": subgroup["name"],
        }
        all_subgroups.append(subgroup_details)
        nested_subgroups = get_all_subgroups(subgroup["id"], root_group_name, level + 1)
        all_subgroups.extend(nested_subgroups)

    return all_subgroups

# Main script execution
if __name__ == "__main__":
    # Fetch the root group details
    root_group_response = requests.get(f"{GITLAB_API_URL}/groups/{ROOT_GROUP_ID}", headers={"PRIVATE-TOKEN": ACCESS_TOKEN})
    root_group_response.raise_for_status()
    root_group = root_group_response.json()
    root_group_name = root_group['name']
    
    all_subgroups = get_all_subgroups(ROOT_GROUP_ID, root_group_name)

    # Convert list of dictionaries to DataFrame
    df = pd.DataFrame(all_subgroups)

    # Fill missing columns to avoid KeyError in DataFrame creation
    max_level = df["Level"].max()
    for level in range(max_level + 1):
        df[f"Level {level} Group Name"] = df.get(f"Level {level} Group Name", "")

    # Drop the Level column as it's no longer needed
    df = df.drop(columns=["Level"])

    # Replace NaN values with blank spaces
    df = df.fillna("")

    # Display all rows and full column content
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_colwidth', None)

    # Print DataFrame
    print(df)

    # Save the DataFrame to an Excel file
    df.to_excel("subgroups_details.xlsx", index=False)
