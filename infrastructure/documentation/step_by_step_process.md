# Step by step devepoler process

1. In the first stage of the development process, we added the following modules:
- Core: contains elements related to all resources:
    - resource group
- databricks: contains elements related to Databricks functionality:
    - Databricks workspace resource
    - Databricks provider
    - Databricks current user resource (this is solely for testing connections between providers)
- storage_security: contains the main functions related to *data lake* storage and its security:
    - storage account
    - *bronze*, *silver*, and *gold* containers
    - Key Vault
    - current user data resource required for Key Vault

2. The second step involves configuring the connection between Databricks and our storage account:
    1. Provision an Azure Databricks access connector (Azure provider): this was done using the `azurerm_databricks_access_connector` resource added to the `storage_security` module.
    2. Assign storage permissions (Azure provider): an `azurerm_role_assignment` was associated with the `storage_security` module.
    3. Create a Unity Catalog storage credential (Databricks provider): `databricks_storage_credential` was added to the `databricks` module, using the Databricks provider.
    4. Map external locations (Databricks provider): `databricks_external_location` was added for the *bronze*, *silver*, *gold*, and *managed* containers (the latter is required for Databricks to store managed tables and to create the catalog resource in the next step) within the `databricks` module.
    5. Define catalogs and schemas (Databricks provider): we added the catalog and schemas to the `databricks` module. 6. If this point is reached, the connection to the storage data lake has been completed.


3. Roadmap for creating Spark jobs to ingest data from APIs into Databricks.
    1. Step 1: Store API Credentials in Azure Key Vault (Terraform)
        This was done by creating the variables to each api, then we add a new secret resource to the `key vault` resource in the storage_security module.
    2. Step 2: Create a Key Vault-Backed Secret Scope (Terraform): To this step we have added the secrets, and the secret scope in the `databricks` module. We have also add a new `azurerm_key_vault_access_policy` to handle the permission needed by the secret scope.
    3. Step 3: Refactor Python Code for Databricks Native Execution: for this step we create the scripts folder with the scripts that will be used in databricks for the ingestion process. 
    4. Step 4: Sync Application Code to Databricks Workspace
    5. Step 5: Provision Databricks Workflows (Jobs) via Terraform

