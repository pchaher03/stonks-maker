terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    databricks = {
      source  = "databricks/databricks"
      version = "1.135.0"
    }
  }

  required_version = ">= 1.0"
}

provider "azurerm" {
  features {}
}

provider "databricks" {
  host = module.databricks.workspace_url
}