
# Setup Guide

1. [Google Cloud Platform](#google-cloud-platform)
2. [Visual Studio Code](#visual-studio-code)
3. [VM Instance](#vm-instance)
4. [Terraform](#terraform)
5. [Airflow](#airflow)
6. [DBT Cloud](#dbt-cloud)

## Google Cloud Platform

1. Create a GCP Account.
2. Create a New Project.  
    Note the `PROJECT_NAME` and the `PROJECT_ID`
3. Create a service account.  
IAM & Admin > Service Accounts > Create Service Account > Grant Service Account Access:
    - Storage Admin
    - BigQuery Admin
    - Compute Admin
    - Storage Object Admin
4. Create a key for the new Service Account.  
    Select the created account in IAM & Admin > Service Accounts.  
    Manage Keys > Add Key > Create new key > Key Type: JSON.  
    The private key is saved on your local machine.  
    Note the location of this .json file.

## Visual Studio Code

1. Install [Visual Studio Code](https://code.visualstudio.com/Download) on your local machine.
2. Install [Remote - SSH extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh) in your Visual Studio Code setup to access your VM instance.
3. Connect to the VM instance later through Visual Studio Code.  
Refer to this [documentation](https://code.visualstudio.com/docs/remote/ssh) for more details. 

## VM Instance

1. Create a new ssh key on your local machine.  
Check this [guide](https://cloud.google.com/compute/docs/connect/create-ssh-keys) depending on your OS.  
For Linux and macOS, replace the `KEY_FILENAME` and the `USERNAME` before running the following on the terminal:
    ```
    ssh-keygen -t rsa -f ~/.ssh/KEY_FILENAME -C USERNAME -b 2048
    ```
2. Create a config file in ~/.ssh.
    ```
    Host <vm-instance-alias>
        HostName <EXTERNAL IP>
        User <USERNAME>
        IdentityFile <~/.ssh/KEY_FILENAME>
    ```
    **Note**: The Host is an alias for the VM Instance. HostName is the `EXTERNAL_IP` of the VM instance on startup. The IdentityFile is the location of the ssh key.
3. Add SSH key in GCP.  
    Enable Compute Engine API.  
    Compute Engine > VM Instances > Enable API  
    Copy the contents of the created public key .pub.  
    Access GCP, Compute Engine > Metadata > Add SSH Key > Paste the contents of .pub > Save
4. Create a VM instance.  
    Compute Engine > VM Instances > Create Instance  
    Name the new VM instance and select a region and a zone.  
    The following are the recommended specifications:
    * Machine Type: e2-standard-4
    * Operating System: Ubuntu
    * Version: Ubuntu 20.04 LTS
    * Boot Disk Type: Balanced Persistent 
    * Boot Disk Size: 30 GB
    Select Create.
5. Check the VM instance.  
    Start the created instance.  
    Compute Engine > VM Instances  
    Copy the `EXTERNAL_IP` after machine creation.
6. Access the VM instance from your local machine.  
    Modify the following script before running:
   ```
   ssh -i ~/.ssh/KEY_FILENAME USERNAME@EXTERNAL_IP
   ```
   
7. Install Anaconda on the VM instance.  
    To download and install anaconda:
    ```
    wget https://repo.anaconda.com/archive/Anaconda3-2023.09-0-Linux-x86_64.sh;
    bash Anaconda3-2023.09-0-Linux-x86_64.sh;
    ```
    Answer yes to the prompt.  
    To update .bashrc without logging out:
    ```
    source .bashrc
    ```
    **Note**: You may use a later version of anaconda.  
8. Install Docker on the VM instance:  
    Run the following:
    ```
    sudo apt-get update
    sudo apt-get install docker.io
    ```
9. Fork and clone this repository. Refer to this [guide](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo).
10. Run docker commands without sudo.  
    Check this [link](https://github.com/sindresorhus/guides/blob/main/docker-without-sudo.md).
11. Install docker compose on the VM instance.  
    Run the following in your home directory:
    ```
    cd ~;
    mkdir bin;
    cd bin;
    wget https://github.com/docker/compose/releases/download/v2.3.4/docker-compose-linux-x86_64 -O docker-compose;
    chmod +x docker-compose;
    ```
    **Note**: You may use a later version of docker compose.  
    Append the following line in your .bashrc:
    ```
    export PATH="${HOME}/bin:${PATH}"
    ```
    Run the following for the changes to take effect:
    ```
    source .bashrc
    ```
12. Install terraform on the VM instance:
    ```
    cd ~/bin;
    sudo apt-get install unzip;
    wget https://releases.hashicorp.com/terraform/1.7.5/terraform_1.7.5_linux_amd64.zip;
    unzip terraform_1.7.5_linux_amd64.zip;
    rm terraform_1.7.5_linux_amd64.zip;
    ```
    **Note**: You may use a later version of terraform.
13. Copy the downloaded .json from the created service account to the VM instance.  
    On your local machine, run the following:
    ```
    sftp <vm-instance-alias>
    ```
    Once inside the VM instance:
    ```
    cd ~;
    mkdir -p .google/credentials;
    cd .google/credentials;
    put <downloaded private key.json>;
    ```
    Exit sftp.  
    Access the VM instance again to rename and authenticate the key file.  
    Run the following:
    ```
    cd ~/.google/credentials;
    mv <downloaded private key.json> google_credentials.json;
    export GOOGLE_APPLICATION_CREDENTIALS=~/.google/credentials/google_credentials.json;
    gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS
    ```

## Terraform
1. Modify variables.tf in the terraform directory of the cloned repository.  
Update the default values of the following variables.  
Also, you may modify the region and location values.  
Note the values for the variables `BQ_DATASET` and `GCP_GCS_BUCKET`.
```
variable "credentials" {
  description = "My Credentials"
  default     = "<Path to your Service Account json file>"
  #ex: if you have a directory where this file is called keys with your service account json file
  #saved there as my-creds.json you could use default = "./keys/my-creds.json"
}

variable "project" {
  description = "Project"
  default     = "<PROJECT_ID>"
}

variable "bq_dataset_name" {
  description = "My BigQuery Dataset Name"
  #Update the below to what you want your dataset to be called
  default     = "<BQ_DATASET>"
}

variable "gcs_bucket_name" {
  description = "My Storage Bucket Name"
  #Update the below to a unique bucket name
  default     = "<GCP_GCS_BUCKET>"
}
```
2. Initialize terraform in the terraform directory.
```
terraform init
```
3. Check the infrastructure that will be created.
```
terraform plan
```
4. Create the GCS Bucket and the BigQuery Dataset.
```
terraform apply
```

## Airflow
The setup for airflow follows the 2022 Cohort [documentation](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2022/week_2_data_ingestion/airflow/1_setup_official.md) (Pre-Reqs) and [execution](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/cohorts/2022/week_2_data_ingestion/airflow)
1. Access the airflow directory of the cloned repository.  
    Run the following commands:
```
    mkdir -p ./dags ./logs ./plugins;
    echo -e "AIRFLOW_UID=$(id -u)" > .env;
```
2. Modify the docker-compose.yml in the airflow directory.  
    Replace the values of the following:  
```      
    GCP_PROJECT_ID: 'PROJECT_ID'  
    GCP_GCS_BUCKET: 'GCP_GCS_BUCKET'
```
3. Update the value of `BQ_DATASET` in the airflow/dags/data_ingestion_gcs_dag.py.
```
    BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'BQ_DATASET')
```
4. Build the airflow image and initialize it.  
    Run the following in the airflow directory:
```
    docker build;
    docker-compose up airflow-init;
    docker-compose up;
```
5. Allow Port Forwarding in VS Code. Forward Port "8080".  
Refer to this [guide](https://code.visualstudio.com/docs/remote/ssh#_forwarding-a-port-creating-ssh-tunnel)
    Access the corresponding forwarded address in your browser.
    Log-in with 'airflow' as your username and your password.

## DBT Cloud
1. Create an account in [dbt](https://www.getdbt.com/product/dbt-cloud).
2. Setup the project.  
    You may watch this [video](https://youtu.be/ueVy2N54lyc?si=gkiSyf-IsYWYGRPb) as a guide.  
    Select the BigQuery connection and upload the google service account credentials downloaded earlier.  Connect your cloned repository using the ssh link.  
    Save the key provided after connecting the repository.  
    Refer to this [link](https://docs.getdbt.com/docs/cloud/git/import-a-project-by-git-url) on how to install it on your git provider.  
    In the Account settings > Projects > Edit, use dbt as the Project subdirectory.
3. In the dbt Cloud IDE, edit the dbt/models/staging/schema.yml based on the values defined earlier.
```
sources:
  - name: staging
    database: PROJECT_ID
    schema: BQ_DATASET
```
4. Deploy a production job to create the models.  
    You may watch this [video](https://youtu.be/V2m5C0n8Gro?si=TfyVTBHBhmo8PN3r) as a guide.  
    Deploy > Environments > Create environment > Set deployment type as Production.  
    In the Production environment, create a job.  
    Deploy Job > Tick the Generate docs on run and Run source freshness > Run on Schedule  
    Trigger the job manually to build the models.
