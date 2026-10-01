module "resource_group" {
  source = "./modules/core"
  project_name = var.project_name
}

module "storage_security" {
  source = "./modules/storage_security"
  project_name = var.project_name
  resource_group_name = module.resource_group.name
  resource_group_location = module.resource_group.location
}

module "databricks" {
  source = "./modules/databricks"
  project_name = var.project_name
  resource_group_name = module.resource_group.name
  resource_group_location = module.resource_group.location
  access_connector_id = module.storage_security.access_connector_id
}