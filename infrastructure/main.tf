resource "azurerm_resource_group" "rg_stonks_maker" {
  name     = "rg-${var.project_name}"
  location = "EAST US"
}

resource "azurerm_storage_account" "storage_account" {
  name                     = "storage${var.project_name}"
  resource_group_name      = azurerm_resource_group.rg_stonks_maker.name
  location                 = azurerm_resource_group.rg_stonks_maker.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  is_hns_enabled           = true

}

resource "azurerm_storage_data_lake_gen2_filesystem" "bronze" {
  name               = "bronze"
  storage_account_id = azurerm_storage_account.storage_account.id
}

resource "azurerm_storage_data_lake_gen2_filesystem" "silver" {
  name               = "silver"
  storage_account_id = azurerm_storage_account.storage_account.id
}

resource "azurerm_storage_data_lake_gen2_filesystem" "gold" {
  name               = "gold"
  storage_account_id = azurerm_storage_account.storage_account.id
}

resource "azurerm_key_vault" "kv" {
  name                        = "kv-dev-${var.project_name}" # Must be globally unique
  location                    = azurerm_resource_group.rg_stonks_maker.location
  resource_group_name         = azurerm_resource_group.rg_stonks_maker.name
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  sku_name                    = "standard"

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    secret_permissions = [
      "Get", "List", "Set", "Delete", "Purge", "Recover"
    ]
  }
}

resource "azurerm_databricks_workspace" "databricks_workspace" {
  name                = "dbx-${var.project_name}"
  resource_group_name = azurerm_resource_group.rg_stonks_maker.name
  location            = azurerm_resource_group.rg_stonks_maker.location
  sku                 = "premium" 
}

data "azurerm_client_config" "current" {}