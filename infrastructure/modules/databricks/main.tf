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

resource "databricks_storage_credential" "external_mi" {
  name = "stonks_storage_credential"
  
  azure_managed_identity {
    access_connector_id = var.access_connector_id
  }
  
  comment = "Managed by Terraform"
}

resource "databricks_external_location" "managed" {
  name            = "managed_location"
  url             = "abfss://managed@storage${var.project_name}.dfs.core.windows.net/"
  credential_name = databricks_storage_credential.external_mi.id
  comment         = "Default Managed Storage for Stonks Catalog"
}

resource "databricks_external_location" "bronze" {
  name            = "bronze_location"
  url             = "abfss://bronze@storage${var.project_name}.dfs.core.windows.net/"
  credential_name = databricks_storage_credential.external_mi.id
  comment         = "Bronze Medallion Layer - Managed by Terraform"
}

resource "databricks_external_location" "silver" {
  name            = "silver_location"
  url             = "abfss://silver@storage${var.project_name}.dfs.core.windows.net/"
  credential_name = databricks_storage_credential.external_mi.id
  comment         = "Silver Medallion Layer - Managed by Terraform"
}

resource "databricks_external_location" "gold" {
  name            = "gold_location"
  url             = "abfss://gold@storage${var.project_name}.dfs.core.windows.net/"
  credential_name = databricks_storage_credential.external_mi.id
  comment         = "Gold Medallion Layer - Managed by Terraform"
}   


resource "databricks_catalog" "stonks_catalog" {
  name    = "stonks_catalog"
  comment = "Main catalog for the Stonks Maker project - Managed by Terraform"
  storage_root = databricks_external_location.managed.url
} 

resource "databricks_schema" "bronze" {
  catalog_name = databricks_catalog.stonks_catalog.name
  name         = "bronze"
  comment      = "Bronze Layer: Raw Data Ingestion (OHLCV & News Feeds)"
  storage_root = databricks_external_location.bronze.url
}

resource "databricks_schema" "silver" {
  catalog_name = databricks_catalog.stonks_catalog.name
  name         = "silver"
  comment      = "Silver Layer: PySpark Transformations (Indicators & Sentiment)"
  storage_root = databricks_external_location.silver.url
}

resource "databricks_schema" "gold" {
  catalog_name = databricks_catalog.stonks_catalog.name
  name         = "gold"
  comment      = "Gold Layer: Feature Matrices (Joined on Date/Ticker)"
  storage_root = databricks_external_location.gold.url
}