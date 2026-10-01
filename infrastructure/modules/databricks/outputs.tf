output "workspace_url" {
  value = azurerm_databricks_workspace.databricks_workspace.workspace_url
}

output "databricks_user_name" {
  value = data.databricks_current_user.me.user_name
}