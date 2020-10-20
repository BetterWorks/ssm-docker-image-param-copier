# Overview

This script is used to copy microservice SSM Docker image parameters from one application to another. The script is very manual. There's no input validation, no error checking/handling. No destructive operations will be made to any SSM parameters, however running this script will create new versions of parameters in Parameter Store if they exist. This is not destructive, the previous version of all parameters will still be accessible.

This script writes parameters to the Parameter Store in the targeted AWS account. The path parameters are written to is `/bw/$account/betterworks-$app_name/cicd/deployment/manifest/`. This script supports parameters both `String` and `SecureString` parameters. 

This script has only been run/tested with Python 3.6.8. It presumably works with other Python 3 versions, however this has not been verified.

---

**Note**: The following assumes we want to copy the microservice SSM Docker image parameters in the sandbox account/environment from an app named sandbox to sandbox5. The instructions and prerequisites would need to be modified to run in other environments, such as champagne, prodeu, or prod.

---

# Prerequisites

* Working `aws-vault` with profile for `betterworks-sandbox-admin`

* `pyenv`

# Instructions

1. Clone the repository

    `git clone git@github.com:BetterWorks/ssm-docker-image-param-copier.git`

2. Create a new virtualenv

   `pyenv virtualenv 3.6.8 ssm-copier`

3. Enter the directory

    `cd ssm-docker-image-param-copier`

4. Activate virtualenv

    `pyenv activate ssm-copier`

5. **Optional**: Make `ssm-copier` virtualenv default Python version

    `pyenv local ssm-copier`

6. Install required modules

    `pip install -r requirements.txt`

7. Start an `aws-vault` session for account/environment

    `aws-vault exec betterworks-sandbox-admin`

8. Run the script

    `python ssm-coper.py -s sandbox -d sandbox5 -e sandbox`
    
    **Note**: In order to use the `latest` tag for all micro serviceas as opposed to what the `sandbox` app is using for all Docker image tag parameters, add the `-l` option. `-l` is all or nothing, so use with caution.

9. End `aws-vault` session

    `exit`
