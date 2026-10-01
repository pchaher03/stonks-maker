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
