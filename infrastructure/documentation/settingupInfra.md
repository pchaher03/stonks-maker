# Requirements 

- Azure CLI
- Terraform

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

