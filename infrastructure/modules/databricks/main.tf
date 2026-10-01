terraform {
  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "1.135.0"
    }
  }
}


resource "azurerm_databricks_workspace" "databricks_workspace" {
  name                = "dbx-${var.project_name}"
  resource_group_name = var.resource_group_name
  location            = var.resource_group_location
  sku                 = "premium" 
}

data "databricks_current_user" "me" {
  depends_on = [azurerm_databricks_workspace.databricks_workspace]
}