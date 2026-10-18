resource "azurerm_resource_group" "rg_stonks_maker" {
  name     = "rg-${var.project_name}"
  location = "EAST US"
}