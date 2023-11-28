# gitlab_updatemr

This script allows updating GitLab merge request (both gitlab.com or self-hosted) with output from previous job.

Typical use case in gitlab-ci.yml file:
```yaml
preview:
  stage: test
  script:
    - date | tee output.txt
    - my-command.sh |tee -a output.txt'
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event" && $CI_MERGE_REQUEST_TARGET_BRANCH_PROTECTED == "true"
  artifacts:
    paths:
      - output.txt

update_mr:
  stage: test
  needs:
    - job: preview
      artifacts: true
  variables: # Optional, can be defined in CI/CD variables as well
    GITLAB_UPDATEMR_SINGLE_THREAD: True # Use always first Discussion thread?
    GITLAB_UPDATEMR_OUTPUT: output.txt # this is the default if unspecified
    GITLAB_UPDATEMR_SYNTAX: yaml # Define syntax highlighting
  script:
    - sed -i 's/\x1b\[[0-9;]*[mGKHF]//g' output.txt # OPTIONAL: if you wish to remove asci chars from output (for example: colored output)
    - /app/update_mr.py
  image: ghcr.io/sysbeetech/gitlab_updatemr:latest
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event" && $CI_MERGE_REQUEST_TARGET_BRANCH_PROTECTED == "true"
```

## Installation

You can use this script in your project, or you can use pre-built docker image. Please see example above.

### Available docker images:

```
docker pull ghcr.io/sysbeetech/gitlab_updatemr:latest
```

```
docker pull sysbee/gitlab_updatemr:latest
```

* `main` - tag will track current main branch
* `latest` - tag will always point to latest release
* `0.1.0` - tag will track releases
* `0.1` - alias to latest 0.1.x tag


### Required configuration

Script requires `GITLAB_UPDATEMR_TOKEN` environment variable with GITLAB_TOKEN that has at least `api` privileges and `Developer` role on the project.

**Note**: Developer role is required when using `GITLAB_UPDATEMR_SINGLE_THREAD` to unresolve thread when it updates it.

You can use either [Personal access tokens](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html) or [Project access tokens](https://docs.gitlab.com/ee/user/project/settings/project_access_tokens.html)

### Optional configuration

Available optional environment variables:

* `GITLAB_UPDATEMR_SINGLE_THREAD` - default: False
    By default `update_mr.py` will always create new thread in GitLab merge requests when new commits are added. If you wish to update only the first thread that  this script creates, set this variable to `True`


* `GITLAB_UPDATEMR_OUTPUT` - default: ./output.txt
    Define the output file used to create discussion thread on MR. Location is relative to project root


* `GITLAB_UPDATEMR_SYNTAX` - default: None
    By default `update_mr.py` will wrap the output.txt file contents in codeblocks with no syntax highlighting. You can set this variable to any [GitLab supported](https://docs.gitlab.com/ee/user/project/highlighting.html) syntax highlighters.
