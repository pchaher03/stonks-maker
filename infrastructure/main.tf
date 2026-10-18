module "resource_group" {
  source = "./modules/core"
  project_name = var.project_name
}

module "storage_security" {
  source = "./modules/storage_security"
  project_name = var.project_name
  resource_group_name = module.resource_group.name
  resource_group_location = module.resource_group.location
  alpha_vantage_api_key = var.alpha_vantage_api_key
  news_api_key = var.news_api_key
}

module "databricks" {
  source = "./modules/databricks"
  project_name = var.project_name
  resource_group_name = module.resource_group.name
  resource_group_location = module.resource_group.location
  access_connector_id = module.storage_security.access_connector_id
  key_vault_id  = module.storage_security.key_vault_id
  key_vault_uri = module.storage_security.key_vault_uri
  git_url = var.git_url
  git_branch = var.git_branch
}