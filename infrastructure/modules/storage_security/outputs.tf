output "access_connector_id" {
  value = azurerm_databricks_access_connector.ext_access_connector.id
}

output "key_vault_id" {
  value = azurerm_key_vault.kv.id
}

output "key_vault_uri" {
  value = azurerm_key_vault.kv.vault_uri
}