# within package/mymodule1.py, for example
import pkgutil
import os
import openai
import shutil
import requests
from datetime import datetime
from base64 import b64encode
from nacl import encoding, public
import time
import json

actions_data = pkgutil.get_data(__name__, "templates/actions.yml")
compose_data = pkgutil.get_data(__name__, "templates/docker-compose.yml")
dockerfile_data = pkgutil.get_data(__name__, "templates/Dockerfile")
server_data = pkgutil.get_data(__name__, "templates/server.py")
readme_data = pkgutil.get_data(__name__, "templates/readme.md")
requirements_data = pkgutil.get_data(__name__, "templates/requirements.txt")
fallback_data = pkgutil.get_data(__name__, "templates/fallback.py")
test_services_data = pkgutil.get_data(__name__, "templates/test_services.py")
test_models_data = pkgutil.get_data(__name__, "templates/test_models.py")
gitignore_data = pkgutil.get_data(__name__, "templates/.gitignore")

def gpt_key(key):
    openai.api_key=key

def githubtoken(token):
    global github_token
    github_token=token


def makeSecret(github_token, repo_owner, repo_name, secret_name, secret_value):
    # Get public key from the GitHub API
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/secrets/public-key"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github+json",
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to get public key: {response.text}")
        return False

    public_key_data = response.json()

    # Encrypt your secret_value using the public key
    public_key = public.PublicKey(public_key_data["key"].encode("utf-8"), encoding.Base64Encoder())
    box = public.SealedBox(public_key)
    encrypted_value = box.encrypt(secret_value.encode("utf-8"))

    # Encode the encrypted value in base64
    encrypted_value_base64 = b64encode(encrypted_value).decode("utf-8")

    # Create the secret using the GitHub API
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/secrets/{secret_name}"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github+json",
    }
    data = {
        "encrypted_value": encrypted_value_base64,
        "key_id": public_key_data["key_id"],
    }
    response = requests.put(url, headers=headers, data=json.dumps(data))

    if response.status_code != 201 and response.status_code != 204:
        print(f"Failed to create secret: {response.text}")
        return False

    print(f"Secret '{secret_name}' created successfully.")
    return True

def github(email, gcp_credentials):
    if not os.path.exists("readme.md"):
        f = open("readme.md", "w")
        f.write(readme_data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n"))
        f.close()
    headers_init = {
    'Authorization': 'Bearer '+github_token,
    }

    response = requests.get('https://api.github.com/user', headers=headers_init)
    #get the name of the parent directory
    repo_name = os.getcwd().split("\\")[-1].title()

    user_name = response.json()['login']
    headers = {
    'Authorization': 'token '+github_token,
    }
    
    data = '{"name": "'+repo_name+'"}'
    
    response = requests.post('https://api.github.com/user/repos', headers=headers, data=data)

    # Add the secrets after creating the repo
    makeSecret(github_token, user_name, repo_name, 'GCP_EMAIL', email)
    makeSecret(github_token, user_name, repo_name, 'GCP_CREDENTIALS', gcp_credentials)

    current_time = datetime.now().strftime("%H:%M:%S")

    #add the .gitignore file
    f = open(".gitignore", "w")
    f.write(gitignore_data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n"))
    
    os.system("git init")
    os.system("git add .")
    os.system("git add .")
    os.system("git reset -- driver.py")
    os.system("git reset -- package/*")
    git_commit_with_time = f'git commit -m "update:{current_time}"'
    os.system(git_commit_with_time)
    os.system("git branch -M main")
    os.system("git remote rm origin")
    os.system("git remote add origin https://github.com/"+user_name+"/"+repo_name+".git")
    os.system("git push -u origin main")

def actions(project_id, app_id):
    #if not created create a .github folder
    if not os.path.exists(".github"):
        os.mkdir(".github")
    #if not created create a workflows folder
    if not os.path.exists(".github/workflows"):
        os.mkdir(".github/workflows")
    #create a file called foo.foo
    f = open(".github/workflows/actions.yml", "w")
    #convert the data to a string
    prefill_actions=actions_data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    #replace the project id
    prefill_actions=prefill_actions.replace("###project_id###", project_id)
    #replace the app id
    prefill_actions=prefill_actions.replace("###app_id###", app_id)
    f.write(prefill_actions)

def docker():
    f = open("docker-compose.yml", "w")
    f.write(compose_data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n"))
    f = open("Dockerfile", "w")
    f.write(dockerfile_data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n"))
    #create file requirements.txt
    with open("requirements.txt", "w") as f:
        f.write(requirements_data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n"))

def server(descriptor):
    #if not created create a app folder
    if not os.path.exists("app"):
        os.mkdir("app")

    #if not created create a models folder
    if not os.path.exists("app/models"):
        os.mkdir("app/models")
    #write test_models.py to app/models
    f = open("app/models/test_models.py", "w")
    f.write(test_models_data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n"))

    #if not created create a controllers folder
    if not os.path.exists("app/services"):
        os.mkdir("app/services")
    #write test_services.py to app/services
    f = open("app/services/test_services.py", "w")
    f.write(test_services_data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n"))
    
    #create __init__.py files
    f = open("app/__init__.py", "w")
    f = open("app/models/__init__.py", "w")
    f = open("app/services/__init__.py", "w")

    #save descriptor to description.txt
    f = open("app/description.txt", "w")
    f.write(descriptor)

    #get the name of the parent directory
    parent_dir = os.getcwd().split("\\")[-1].title()
    server_file=server_data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")+"\n\n\n"
    server_file=server_file.replace("___title___", parent_dir)

    #write server file to autocontroller.py
    f = open("app/autocontroller.py", "w")
    f.write(server_file)

    #write fallback file to fallback.py
    f = open("app/fallback.py", "w")
    f.write(fallback_data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n"))
     
def wipe():
    #delete app folder
    shutil.rmtree("app")
    #delete .github folder
    shutil.rmtree(".github")
    #delete docker-compose.yml
    os.remove("docker-compose.yml")
    #delete Dockerfile
    os.remove("Dockerfile")
    #delete requirements.txt
    os.remove("requirements.txt")
    #delete readme.md
    os.remove("readme.md")

def stage():
    headers_init = {
    'Authorization': 'Bearer '+github_token,
    }

    response = requests.get('https://api.github.com/user', headers=headers_init)
    #get the name of the parent directory
    repo_name = os.getcwd().split("\\")[-1].title()
    user_name = response.json()['login']
    #start chrome and go to localhost:5000
    os.system("start chrome github.com/"+user_name+"/"+repo_name)
    #run docker-compose up
    os.system("docker-compose up")
