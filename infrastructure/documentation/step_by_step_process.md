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
    2. Assign storage permissions (Azure provider): an `azurerm_role_assignment` resource was associated with the `storage_security` module.
    3. Create a Unity Catalog storage credential (Databricks provider): a `databricks_storage_credential` was added to the `databricks` module, using the Databricks provider.
    4. Map external locations (Databricks provider): a `databricks_external_location` was added for the *bronze*, *silver*, *gold*, and *managed* containers (the latter is required for Databricks to store managed tables and to create the catalog resource in the next step) within the `databricks` module.
    5. Define catalogs and schemas (Databricks provider): we added the catalog and schemas to the `databricks` module. 6. At this point, the connection to the storage data lake is complete.


3. Roadmap for creating Spark jobs to ingest data from APIs into Databricks.
    1. Step 1: Store API credentials in Azure Key Vault (Terraform)
    This was done by creating variables for each API and adding a new secret resource to the `key vault` resource in the `storage_security` module.
    2. Step 2: Create a Key Vault-backed secret scope (Terraform): in this step, we added the secrets and the secret scope to the `databricks` module. We also added a new access policy (`azurerm_key_vault_access_policy`) to manage the permissions required for the secrets scope.
    3. Step 3: Refactor the Python code for native execution in Databricks: for this step, we created a `scripts` folder containing the scripts to be used in Databricks for the ingestion process. 4. Step 4: Synchronize the application code with the Databricks workspace: we added a Git repository resource to the `databricks` module to synchronize the code running in Databricks with the code in the repository.
    5. Step 5: Provision Databricks workflows (Jobs) using Terraform: we just added a new job that executes the ingestion scripts.

4. Workflow activation process
    There are several ways to execute the workflow:
    2. via manual activation.
    3. it will run daily at 18:00.

Script considerations
1. For `databricks_ohlcv_ingestion.py`, it is necessary to set `outputsize="full"` initially to download one year's worth of data; subsequently, it should be changed to `outputsize="compact"` for daily downloads.