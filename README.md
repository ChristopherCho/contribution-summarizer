# Contribution Summarizer
This script will summarize the contributions of a user in a given repositories. It will count the number of commits, opened PRs and commented PRs made by the user.

### Output example
```
Repository1: 
        - Commits: 736
        - Opened PRs: 64
        - Commented PRs: 106

Repository2: 
        - Commits: 90
        - Opened PRs: 22
        - Commented PRs: 12

...

Total: 
        - Commits: 1090
        - Opened PRs: 123
        - Commented PRs: 167
```


## Installation
1. Clone the repository
2. Install the requirements
    ```
    pip install -r requirements.txt
    ```
3. Install Github CLI following the instructions [here](https://cli.github.com/manual/installation)

## Data Preparation
1. Create a file named `repositories.json` in the `data` directory. The file should look like this:
    ```
    {
        "<USER_REPO_NAME>": "git@github.com:<USER_NAME>/<REPOSITORY_NAME>.git",
        "<ORG_REPO_NAME>": "git@github.com:<ORG_NAME>/<REPOSITORY_NAME>.git",
        ...
    }
    ```
    `<USER_REPO_NAME>` or `<ORG_REPO_NAME>` could be any name you want to give to the repository. The name will be used in the output. The value "git@github.com:..." is the repository URL. You can find the repository URL by clicking on the "Code" button on the repository page and then clicking on "SSH". The URL should look like this:
    ```
    git@github.com:ChristopherCho/contribution-summarizer.git
    ```

2. Create a Github Personal Access Token following the instructions [here](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token) You will need to select the following scopes:
    - repo
    - user
3. Create a file named `token.txt` and paste the token in the file. The file should look like this:
    ```
    <your token>
    ```
    You can just run the main program and it will ask you for the token if the file is not found.

## Usage
Run the main program
```
python main.py -u <USER_NAME>
```

### Options
```
usage: main.py [-h] --username USERNAME [--search_limit SEARCH_LIMIT] [--cache_dir CACHE_DIR] [--repository_info_path REPOSITORY_INFO_PATH] [--access_token_file ACCESS_TOKEN_FILE]

optional arguments:
  -h, --help            show this help message and exit
  --username USERNAME, -u USERNAME
                        GitHub username to check contribution.
  --search_limit SEARCH_LIMIT
                        Limit the number of search results. (default: 10000)
  --cache_dir CACHE_DIR
                        Path to cache directory where repositories are cloned. (default: .cache/repos/)
  --repository_info_path REPOSITORY_INFO_PATH
                        Path to repository info file. (default: data/repositories.json)
  --access_token_file ACCESS_TOKEN_FILE
                        Path to Github access token file. (default: data/token.txt)
```