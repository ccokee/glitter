# GLITTER: Repository Auto-Updater

This project provides a Dockerized Python script that automatically updates Git repositories. It traverses specified directories, checks for changes, commits, and pushes them to the remote repository. If there are no changes, it updates or creates a `README.md` file with a timestamp. The script runs on a schedule defined by a cron expression.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [Project Structure](#project-structure)
  - [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
- [Usage](#usage)
  - [Building the Docker Image](#building-the-docker-image)
  - [Running the Docker Container](#running-the-docker-container)
- [Script Behavior](#script-behavior)
- [Cron Schedule](#cron-schedule)
- [Logging](#logging)
- [Security Considerations](#security-considerations)
- [Additional Notes](#additional-notes)
- [License](#license)

---

## Features

- **Automatic Repository Updates**: Traverses directories to find Git repositories belonging to a specified user and updates them.
- **Commit Changes**: Commits and pushes changes with a formatted message.
- **README Timestamping**: Updates or creates a `README.md` with the last update timestamp if there are no changes.
- **Cron Scheduling**: Runs the update script on a schedule specified via a cron expression.
- **Multi-Git Provider Support**: Works with GitHub, GitLab, or Bitbucket repositories.

---

## Prerequisites

- **Docker** installed on your system.
- **Docker Compose** installed.
- **SSH Keys** configured for authentication with your Git provider.
- **Access** to the repositories you wish to update.

---

## Getting Started

### Project Structure

```
project_root/
├── update_repos.py
├── Dockerfile
├── entrypoint.sh
├── docker-compose.yml
└── .env
```

### Configuration

1. **Clone or Download** the project files into a directory (`project_root`).

2. **Set Up SSH Authentication**:
   - Ensure your SSH keys are correctly set up and have access to the repositories.
   - The `SSH_DIR` variable in the `.env` file should point to your local `.ssh` directory.

3. **Configure Environment Variables**:
   - Update the `.env` file with your specific configuration.
   - Ensure all paths and variables are correctly set.

### Environment Variables

The `.env` file contains the configuration for the project. Below is an explanation of each variable:

```dotenv
# Local path you want to mount (your repositories directory)
LOCAL_DIR=/path/to/your/directory

# Directory inside the container where the directory will be mounted
MOUNTED_DIR=/githubdirs

# Your GitHub, GitLab, or Bitbucket username
GIT_USER=your_git_username

# Git provider domain (default is github.com)
GIT_PROVIDER=github.com

# Local SSH directory to be mounted into the container
SSH_DIR=/home/your_username/.ssh

# Cron schedule in standard cron format (e.g., '0 0 * * *' for daily at midnight)
CRON_SCHEDULE=0 0 * * *  # Every day at midnight
```

---

## Usage

### Building the Docker Image

Open a terminal in the `project_root` directory and run:

```bash
docker-compose build
```

### Running the Docker Container

Start the container with:

```bash
docker-compose up
```

The script will now run according to the cron schedule specified in the `.env` file.

---

## Script Behavior

1. **Repository Traversal**:
   - The script scans all first-level subdirectories in `MOUNTED_DIR`.
   - It identifies Git repositories belonging to `GIT_USER` on `GIT_PROVIDER`.

2. **Handling Changes**:
   - **With Uncommitted Changes**:
     - Adds all changes.
     - Commits with a message in the format `"dd/mm/yyyy auto update"`.
     - Pushes to the `origin`.
   - **Without Uncommitted Changes**:
     - Updates or creates a `README.md` with a timestamp (`"dd/mm/yyyy HH:MM:SS"`).
     - Commits and pushes the `README.md`.

3. **Logging**:
   - Outputs messages indicating progress and any errors.
   - Logs are viewable in the console and the `cron.log` file inside the container.

---

## Cron Schedule

- **Setting the Schedule**:
  - Define `CRON_SCHEDULE` in the `.env` file using standard cron syntax.
  - Example schedules:
    - Every day at midnight: `0 0 * * *`
    - Every hour: `0 * * * *`
    - Every 15 minutes: `*/15 * * * *`

- **Cron Syntax Reference**:
  - `* * * * *` — Every minute.
  - `0 * * * *` — At minute 0 past every hour.
  - `0 0 * * *` — At 00:00 every day.
  - For help crafting expressions, refer to [crontab.guru](https://crontab.guru/).

---

## Logging

- **Cron Output**:
  - Cron job outputs are redirected to `/var/log/cron.log` inside the container.
  - The `tail` command keeps the container running and outputs logs in real-time.

- **Viewing Logs**:
  - Logs are visible in the terminal running `docker-compose up`.
  - For detailed logs, you can access the `cron.log` file inside the container.

---

## Security Considerations

- **SSH Keys**:
  - Your SSH keys are mounted into the container for authentication.
  - Ensure the container environment is secure and trusted.
  - **Alternative Methods**:
    - Use SSH agent forwarding.
    - Use environment variables for personal access tokens.

- **Permissions**:
  - Verify that the user inside the container has permissions to read/write to the mounted directories.

- **Network Access**:
  - Ensure the container has network access to communicate with your Git provider.

---

## Additional Notes

- **Multi-Git Provider Support**:
  - Set `GIT_PROVIDER` to match your provider's domain (e.g., `gitlab.com` or `bitbucket.org`).

- **Script Customization**:
  - You can modify `update_repos.py` to adjust behavior as needed.

- **Docker Compose Service Name**:
  - The service is named `updater` in `docker-compose.yml`. Adjust as necessary.

- **Line Endings and Permissions**:
  - Ensure scripts have the correct line endings (`LF` for Unix/Linux).
  - Set execute permissions for `entrypoint.sh`:
    ```bash
    chmod +x entrypoint.sh
    ```

---

## License

This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute this software as per the terms of the license.

---

**Disclaimer**: This project is provided "as is" without warranty of any kind. Use at your own risk.

---

## Contact

For any questions or issues, please open an issue in the repository or contact the maintainers.

---

**Happy Coding!**

# Appendix: File Contents

Below are the contents of the files included in the project.

---

## `update_repos.py`

```python
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
```

---

## `Dockerfile`

```dockerfile
FROM python:3.9-slim

# Install git and cron
RUN apt-get update && apt-get install -y git cron && rm -rf /var/lib/apt/lists/*

# Copy the script and entrypoint
COPY update_repos.py /usr/local/bin/update_repos.py
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /usr/local/bin/update_repos.py /entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]
```

---

## `entrypoint.sh`

```bash
#!/bin/bash

# Write environment variables to a file so cron can access them
printenv | grep -v "no_proxy" >> /etc/environment

# Set up the cron schedule
CRON_SCHEDULE="${CRON_SCHEDULE:-0 * * * *}"  # Default to every hour if not set

echo "Setting up cron job with schedule: $CRON_SCHEDULE"

# Write out the cron job
echo "$CRON_SCHEDULE /usr/bin/python /usr/local/bin/update_repos.py >> /var/log/cron.log 2>&1" > /etc/cron.d/update_repos_cron

# Give execution rights on the cron job file
chmod 0644 /etc/cron.d/update_repos_cron

# Apply the cron job
crontab /etc/cron.d/update_repos_cron

# Create the log file to be able to run tail
touch /var/log/cron.log

# Start cron and tail the log file
echo "Starting cron..."

cron && tail -f /var/log/cron.log
```

---

## `docker-compose.yml`

```yaml
version: '3'
services:
  updater:
    build: .
    env_file: .env
    volumes:
      - ${LOCAL_DIR}:${MOUNTED_DIR}
      - ${SSH_DIR}:/root/.ssh:ro
```

---

## `.env`

```dotenv
# Local path you want to mount (your repositories directory)
LOCAL_DIR=/path/to/your/directory

# Directory inside the container where the directory will be mounted
MOUNTED_DIR=/githubdirs

# Your GitHub, GitLab, or Bitbucket username
GIT_USER=your_git_username

# Git provider domain (default is github.com)
GIT_PROVIDER=github.com

# Local SSH directory to be mounted into the container
SSH_DIR=/home/your_username/.ssh

# Cron schedule in standard cron format (e.g., '0 0 * * *' for daily at midnight)
CRON_SCHEDULE=0 0 * * *  # Every day at midnight
```

---

**Note**: Replace `/path/to/your/directory`, `your_git_username`, `github.com`, and `/home/your_username/.ssh` with your actual paths and information.

---

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

---

## Acknowledgments

- Thanks to the open-source community for tools and resources that made this project possible.

---

**End of README**