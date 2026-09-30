resource "azurerm_resource_group" "Stonks_maker" {
  name     = "rg-${var.project_name}"
  location = "EAST US"
}