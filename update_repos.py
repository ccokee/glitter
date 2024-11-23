import os
import subprocess
import datetime
import re
import sys

def main():
    MOUNTED_DIR = os.getenv('MOUNTED_DIR', '/githubdirs')
    GIT_USER = os.getenv('GIT_USER')
    GIT_PROVIDER = os.getenv('GIT_PROVIDER', 'github.com')

    if not GIT_USER:
        print("The environment variable GIT_USER is not defined.")
        sys.exit(1)

    if not os.path.isdir(MOUNTED_DIR):
        print(f"The mounted directory {MOUNTED_DIR} does not exist.")
        sys.exit(1)

    for item in os.listdir(MOUNTED_DIR):
        item_path = os.path.join(MOUNTED_DIR, item)
        if os.path.isdir(item_path):
            git_dir = os.path.join(item_path, '.git')
            if os.path.isdir(git_dir):
                # It's a git repository
                os.chdir(item_path)
                try:
                    remote_url = subprocess.check_output(['git', 'remote', 'get-url', 'origin']).decode().strip()
                except subprocess.CalledProcessError:
                    print(f"Failed to get the remote URL of {item_path}")
                    continue

                # Extract the user from the remote repository URL
                pattern_ssh = re.compile(r'git@' + re.escape(GIT_PROVIDER) + ':(.+?)/.+?(\.git)?$')
                pattern_https = re.compile(r'https://' + re.escape(GIT_PROVIDER) + '/(.+?)/.+?(\.git)?$')
                match = pattern_ssh.match(remote_url) or pattern_https.match(remote_url)
                if match:
                    repo_user = match.group(1)
                    if repo_user == GIT_USER:
                        # Check for uncommitted changes
                        status_output = subprocess.check_output(['git', 'status', '--porcelain']).decode().strip()
                        if status_output:
                            # There are changes
                            try:
                                subprocess.check_call(['git', 'add', '.'])
                                date_str = datetime.datetime.now().strftime('%d/%m/%Y auto update')
                                subprocess.check_call(['git', 'commit', '-m', date_str])
                                subprocess.check_call(['git', 'push', 'origin'])
                                print(f"Repository updated with changes: {item_path}")
                            except subprocess.CalledProcessError:
                                print(f"Failed to commit and push changes in {item_path}")
                        else:
                            # No changes, update README.md
                            readme_path = os.path.join(item_path, 'README.md')
                            date_str = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                            timestamp_line = f'Last update: {date_str}\n'
                            if os.path.exists(readme_path):
                                with open(readme_path, 'r') as f:
                                    lines = f.readlines()
                                # Replace or add the timestamp
                                if lines and lines[-1].startswith('Last update:'):
                                    lines[-1] = timestamp_line
                                else:
                                    lines.append('\n' + timestamp_line)
                                with open(readme_path, 'w') as f:
                                    f.writelines(lines)
                            else:
                                # Create README.md with the timestamp
                                with open(readme_path, 'w') as f:
                                    f.write('# README\n\n')
                                    f.write(timestamp_line)
                            # Commit and push
                            try:
                                subprocess.check_call(['git', 'add', 'README.md'])
                                date_commit_msg = datetime.datetime.now().strftime('%d/%m/%Y auto update')
                                subprocess.check_call(['git', 'commit', '-m', date_commit_msg])
                                subprocess.check_call(['git', 'push', 'origin'])
                                print(f"README.md updated in the repository: {item_path}")
                            except subprocess.CalledProcessError:
                                print(f"Failed to commit and push README.md in {item_path}")
                    else:
                        print(f"The repository {item_path} does not belong to the user {GIT_USER}, skipping.")
                else:
                    print(f"Could not parse the remote URL '{remote_url}' in {item_path}")
            else:
                print(f"{item_path} is not a git repository.")
        else:
            print(f"{item_path} is not a directory.")

if __name__ == '__main__':
    main()
