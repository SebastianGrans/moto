#!/bin/bash

if [[ -z ${GITHUB_TOKEN} ]]
then
    echo "Githubs API requires a token. Define the environment variable GITHUB_TOKEN: 'GITHUB_TOKEN : \$\{\{ secrets.GITHUB_TOKEN \}\}' in your workflow's main.yml."
    exit 1
fi

if [[ ${GITHUB_EVENT_NAME} != "pull_request" ]]
then
    echo "This action runs only on pull request events."
    exit 1
fi


apt update
apt install -y curl jq python3 python3-pip
pip install black

github_pr_url=`jq '.pull_request.url' ${GITHUB_EVENT_PATH}`
echo "The event path: ${GITHUB_EVENT_PATH}"
echo "The pull request url: ${github_pr_url}"

# github pr url sometimes has leading and trailing quotes
github_pr_url=`sed -e 's/^"//' -e 's/"$//' <<<"$github_pr_url"`
echo "Downloading PR diff from: ${github_pr_url}"
curl --request GET --url ${github_pr_url}.diff --header "authorization: Bearer ${GITHUB_TOKEN}" --header "Accept: application/vnd.github.v3.diff" > github_diff.txt
echo "Done."
cat github_diff.txt
diff_length=`wc -l github_diff.txt`
echo "Approximate diff size: ${diff_length}"
all_changed_files=`cat github_diff.txt | grep -E -- "\+\+\+ |\-\-\- " | awk '{print $2}'`
echo "All files listed in the PR: ${all}"
python_files=`echo "${all_changed_files}" | grep -Po -- "(?<=[ab]/).+\.py$"`
echo "Python files edited in this PR: ${python_files}"

if [[ -z "${LINE_LENGTH}" ]]; then
    line_length=130
else
    line_length="${LINE_LENGTH}"
fi

black --line-length ${line_length} --check ${python_files}