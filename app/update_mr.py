#!/usr/bin/env python3
import gitlab
import os
import sys

# Get required environment variables

# Required pipeline built-in environment
try:
    server = os.environ["CI_SERVER_HOST"]
    mr_iid = os.environ["CI_MERGE_REQUEST_IID"]
    project_id = os.environ["CI_MERGE_REQUEST_PROJECT_ID"]
    project_dir = os.environ["CI_PROJECT_DIR"]
except KeyError as e:
    sys.exit(f"Unable to detect required {e} environment variable")

# Custom environment variables

# API token with `api` privileges and `Developer` role on projects
try:
    token = os.environ["GITLAB_UPDATEMR_TOKEN"]
except KeyError as e:
    sys.exit(f"Please define {e} environment variable")
# Should the bot always update its first Discussion upon re-runs?
update_thread = os.getenv("GITLAB_UPDATEMR_SINGLE_THREAD", False)
# Define path to output file relative to CI_PROJECT_DIR
output = os.getenv("GITLAB_UPDATEMR_OUTPUT", "output.txt")
# Define ouptut content syntax highlighting
syntax = os.getenv("GITLAB_UPDATEMR_SYNTAX", None)


gl = gitlab.Gitlab(url=f"https://{server}", private_token=token)
gl.auth()
current_user = gl.user
project = gl.projects.get(project_id)
mr = project.mergerequests.get(mr_iid)

# Get Discussions
discussions = mr.discussions.list()
threads = [d for d in discussions if not d.attributes["individual_note"]]


def build_body():
    """
    Returns formatted body for MR discussion creation based on defined
    outputs file and syntax highlighting

        Returns:
            output (str)
    """
    output_file = os.path.join(project_dir, output)
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            content = f.read()
            return f"```{syntax}\n" + content + "\n```"
    else:
        print(f"WARNING: output file {output} not found in project dir")
        return "\n**WARNING**: No previous command output files found"


def find_my_thread(threads):
    """
    Returns first thread created by bot user if it exists

        Parameters:
            threads (list): - list of Discussion threads for MR
        Returns:
            t.id (str): - string containing thread id created by the bot

    """
    username = current_user.attributes["username"]
    for t in threads:
        thread = mr.discussions.get(t.id)
        if thread.attributes["notes"][0]["author"]["username"] == username:
            return t.id
    return False


def update_discussion(thread):
    """
    Updates the existing discussion note body started by the bot

        Parameters:
            thread (str): - thread id string
    """
    discussion = mr.discussions.get(thread)
    first_note_id = discussion.attributes["notes"][0]["id"]
    first_note = discussion.notes.get(first_note_id)
    first_note.body = build_body()
    first_note.save()


def unresolve_discussion(thread):
    """
    Updates the existing discussion resolved status to False

        Parameters:
            thread (str): - thread id string
    """
    discussion = mr.discussions.get(thread)
    discussion.resolved = False
    discussion.save()


def create_thread():
    """
    Creates a new discussion thread on MR with note built from output
    """
    mr.discussions.create({"body": build_body()})


def update_first_thread():
    """
    Creates or Update discussion thread on MR
    """
    thread = find_my_thread(threads)

    if thread:
        unresolve_discussion(thread)
        update_discussion(thread)
    else:
        create_thread()


if update_thread:
    update_first_thread()
else:
    create_thread()
