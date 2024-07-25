import os
import time
import subprocess

import gitlab

from dotenv import load_dotenv


load_dotenv()

GITLAB_URL = os.getenv('GITLAB_URL')
GITLAB_TOKEN = os.getenv('GITLAB_TOKEN')
GITLAB_PROJECT_ID = int(os.getenv('GITLAB_PROJECT_ID'))

gl = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_TOKEN)

project = gl.projects.get(GITLAB_PROJECT_ID)

class GitLabMonitor:
    def __init__(self, project):
        self.project = project
        self.last_commit_id = None
        self.last_mr_id = None

    def track_new_commits(self):
        commits = self.project.commits.list(ref_name='main', per_page=1)
        if commits:
            commit = commits
            if commit.id != self.last_commit_id:
                print(f'New commit detected: {commit.id}')
                self.last_commit_id = commit.id
                self.run_semgrep()
                self.run_linters()

    def track_new_merge_requests(self):
        mrs = self.project.mergerequests.list(state='opened', per_page=1)
        if mrs:
            mr = mrs
            if mr.id != self.last_mr_id:
                print(f'New merge request detected: {mr.id}')
                self.last_mr_id = mr.id
                self.run_semgrep()
                self.run_linters()

    def run_semgrep(self):
        print('Running Semgrep...')
        subprocess.run(['semgrep', '--config', 'path/to/semgrep/config', 'path/to/project'])

    def run_linters(self):
        print('Running linters...')
        subprocess.run(['linters', '--config', 'path/to/linters/config', 'path/to/project'])

monitor = GitLabMonitor(project)
while True:
    monitor.track_new_commits()
    monitor.track_new_merge_requests()
    time.sleep(60)