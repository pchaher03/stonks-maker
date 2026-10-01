resource "azurerm_databricks_workspace" "databricks_workspace" {
  name                = "dbx-${var.project_name}"
  resource_group_name = var.project_name
  location            = var.resource_group_location
  sku                 = "premium" 
}