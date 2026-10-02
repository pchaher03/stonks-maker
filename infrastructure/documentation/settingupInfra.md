# Requirements 

- Azure CLI
- Terraform
- Github

# login using
```bash
az login
```

Verify your account settings with this commands, this is just to verify that your Azure CLI is working.
```bash
az account show

az account list --output table
```

You can select the subscription that you want with:
```bash
az account set --subscription "<SUBSCRIPTION_ID>"
```

An important distintions is that you don't need to save credential to use terraform, The azure CLI maintains your authenticated session locally just after `az login`.


# Repo requirements

Databricks pulls scripts directly from a Git repository, and the daily data download requires updating a few lines. Therefore, for the changes to actually take effect in Databricks, you must create a new repository with the current configuration and update the line via a *commit*. You will find further explanations in the [setupProject.md](./setupProject.md) file.