import os
import json
import argparse

from getpass import getpass
from collections import defaultdict
from tqdm import tqdm


def setup_arguments(args):
    if not os.path.exists(args.cache_dir):    
        os.makedirs(args.cache_dir, exist_ok=True)
    cache_dir = args.cache_dir
        
    if not os.path.isfile(args.access_token_file):
        print(f"Access token file ({args.access_token_file}) not found. Creating one...")
        access_token_file_path = input("Input access token file path (./data/token.txt): ")
        if access_token_file_path != "":
            access_token_file = access_token_file_path
        access_token = ""
        while (access_token == ""):
            access_token = getpass("Input access token: ")
            
        with open(access_token_file, "w") as f:
            f.write(access_token)
            f.close()
        print(f"Access token file created at {access_token_file}")
    else:
        access_token_file = args.access_token_file
    access_token_file = os.path.abspath(access_token_file)
        
    if not os.path.isfile(args.repository_info_path):
        print(f"Repository info file ({args.repository_info_path}) not found.")
        exit(1)
    else:
        repos = json.load(open(args.repository_info_path, "r"))
        
    username = args.username
    
    return cache_dir, access_token_file, repos, username
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", "-u", type=str, required=True, help="GitHub username to check contribution.")
    parser.add_argument("--search_limit", type=int, default=10000, help="Limit the number of search results. (default: 10000)")
    parser.add_argument("--cache_dir", type=str, default=".cache/repos/", help="Path to cache directory where repositories are cloned. (default: .cache/repos/)")
    parser.add_argument("--repository_info_path", type=str, default="data/repositories.json", help="Path to repository info file. (default: data/repositories.json)")
    parser.add_argument("--access_token_file", type=str, default="data/token.txt", help="Path to Github access token file. (default: data/token.txt)")
    
    args = parser.parse_args()
    
    cache_dir, access_token_file, repos, username = setup_arguments(args)
    
    print("Setup repositories...")
    for repo_name, repo_url in tqdm(repos.items()):
        repo_dir = os.path.join(cache_dir, repo_name)
        if not os.path.exists(repo_dir):
            os.system(f"git clone {repo_url} {repo_dir} --quiet")
        else:
            os.system(f"cd {repo_dir} && git pull -q")
    
    print("Analyzing commits and PRs...")
    result_dict = defaultdict(dict)
    for repo_name, repo_url in tqdm(repos.items()):
        repo_dir = os.path.join(cache_dir, repo_name)
        
        # Step 1. Count commits
        # Get the number of commits from user
        results = os.popen(f"cd {repo_dir} && git shortlog -s -n --all --no-merges | grep {username}").readlines()
        if len(results) > 0:
            total_commits = sum([int(result.split()[0]) for result in results])
        else:
            total_commits = 0
            
        result_dict[repo_name]["commits"] = total_commits
        
        # Step 2. Count PRs opened by user
        initial_trial = os.popen(
            f"cd {repo_dir} && "
            f"gh auth login --with-token < {access_token_file} && "
            f"gh pr list -s all --json number --limit 1 -A {username}").readlines()
        initial_trial = json.loads(" ".join(initial_trial))
        if len(initial_trial) > 0:        
            my_prs = os.popen(
                f"cd {repo_dir} && "
                f"gh auth login --with-token < {access_token_file} && "
                f"gh pr list -s all --json number --limit {args.search_limit} -A {username}").readlines()
            my_prs = json.loads(" ".join(my_prs))
            my_prs = [int(pr["number"]) for pr in my_prs]
        else:
            my_prs = []
        result_dict[repo_name]["opened_prs"] = len(my_prs)
        
        # Step 3. Count commented PRs by user
        initial_trial = os.popen(
            f"cd {repo_dir} && "
            f"gh auth login --with-token < {access_token_file} && "
            f"gh pr list -s all --limit 1 --json number -S "
            f"\"commenter:{username} -author:{username}\"").readlines()
        initial_trial = json.loads(" ".join(initial_trial))
        initial_trial = [int(pr["number"]) for pr in initial_trial]
        if len(initial_trial) > 0:
            commented_prs = os.popen(
                f"cd {repo_dir} && "
                f"gh auth login --with-token < {access_token_file} && "
                f"gh pr list -s all --limit {args.search_limit} --json number -S "
                f"\"commenter:{username} -author:{username}\"").readlines()
            commented_prs = json.loads(" ".join(commented_prs))
            commented_prs = [int(pr["number"]) for pr in commented_prs]
        else:
            commented_prs = []

        result_dict[repo_name]["commented_prs"] = len(commented_prs)

    for repo_name, result in result_dict.items():
        print(
            f"{repo_name}: \n"
            f"\t- Commits: {result['commits']}\n"
            f"\t- Opened PRs: {result['opened_prs']}\n"
            f"\t- Commented PRs: {result['commented_prs']}\n"
        )

    print(
        f"Total: \n"
        f"\t- Commits: {sum([result['commits'] for result in result_dict.values()])}\n"
        f"\t- Opened PRs: {sum([result['opened_prs'] for result in result_dict.values()])}\n"
        f"\t- Commented PRs: {sum([result['commented_prs'] for result in result_dict.values()])}\n"
    )