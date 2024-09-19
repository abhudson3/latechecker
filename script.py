import os
import subprocess
from datetime import datetime, timezone, timedelta


# The given date in CST (without timezone in the string)
cutoff_date_str = input("Please input the cutoff date in the following format: 2024-09-05 11:00 AM\n")
cutoff_date_naive = datetime.strptime(cutoff_date_str, "%Y-%m-%d %I:%M %p")

# To handle both cases dynamically:
def is_dst():
    """Determine if Daylight Saving Time (DST) is currently in effect in Central Time"""
    now = datetime.now()
    dst_start = datetime(now.year, 3, 8, 2)  # DST starts second Sunday in March
    dst_end = datetime(now.year, 11, 1, 2)  # DST ends first Sunday in November
    return dst_start <= now < dst_end

# Adjust UTC offset based on DST
utc_offset = -5 if is_dst() else -6
cutoff_date = cutoff_date_naive.replace(tzinfo=timezone(timedelta(hours=utc_offset))).astimezone(timezone.utc)

def get_latest_commit_date(repo_path):
    try:
        # Run git command to get the latest commit date in ISO 8601 format (UTC)
        git_log_command = ["git", "-C", repo_path, "log", "-1", "--format=%cI"]
        result = subprocess.run(git_log_command, capture_output=True, text=True, check=True)
        latest_commit_date_str = result.stdout.strip()
        if latest_commit_date_str:
            # Convert to datetime object in UTC
            latest_commit_date = datetime.fromisoformat(latest_commit_date_str)
            return latest_commit_date
        else:
            print(f"No commits found in '{repo_path}'")
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving commits for '{repo_path}': {e}")
        return None

def check_repos_for_commit_later_than_cutoff():
    current_dir = os.getcwd()
    
    for folder_name in os.listdir(current_dir):
        folder_path = os.path.join(current_dir, folder_name)
        
        if os.path.isdir(folder_path):
            git_folder = os.path.join(folder_path, ".git")
            
            # Check if this folder contains a Git repository
            if os.path.isdir(git_folder):
                latest_commit_date = get_latest_commit_date(folder_path)
                
                if latest_commit_date and latest_commit_date > cutoff_date:
                    print(f"Repository '{folder_name}' has a commit after the cutoff date: {latest_commit_date}")
            else:
                print(f"'{folder_name}' is not a git repository.")

if __name__ == "__main__":
    check_repos_for_commit_later_than_cutoff()
