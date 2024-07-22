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
def get_all_subgroups(group_id, parent_info=[], level=0, is_level_1=False):
    all_subgroups = []
    total_count = 0
    page = 1
    while True:
        subgroups, headers = get_subgroups(group_id, page)
        for subgroup in subgroups:
            if level == 1:
                is_level_1 = True

            current_info = parent_info + [subgroup["name"]]
            if not is_level_1:
                total_count += 1

            subgroup_details = {
                "Level 1 Group Name": parent_info[0] if parent_info else "",
                "Hierarchical Path": " / ".join(current_info)
            }
            all_subgroups.append(subgroup_details)
            nested_subgroups, nested_count = get_all_subgroups(subgroup["id"], current_info, level + 1, is_level_1)
            all_subgroups.extend(nested_subgroups)
            total_count += nested_count
        if 'X-Next-Page' in headers and headers['X-Next-Page']:
            page = int(headers['X-Next-Page'])
        else:
            break
    return all_subgroups, total_count

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

    # Display all rows and full column content
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_colwidth', None)

    # Print DataFrame
    print(df)

    # Save the DataFrame to an Excel file
    df.to_excel("subgroups_details.xlsx", index=False)

    # Print total count of subgroups
    print(f"Total number of subgroups excluding level 1 group names: {total_count}")
