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

resource "databricks_secret_scope" "kv_scope" {
  name = "stonks_secrets"

  keyvault_metadata {
    resource_id = var.key_vault_id
    dns_name    = var.key_vault_uri
  }
}

resource "databricks_repo" "stonks_maker_repo" {
  # The URL to your GitHub repository
  url    = "https://github.com/pchaher03/stonks-maker.git"
  branch = "feat-terraform"
  # Optional: You can specify a specific path in the workspace. 
  # If omitted, Databricks creates it in your user's Repo folder automatically.
}

data "databricks_node_type" "available_node" {
  local_disk    = true
  min_cores     = 4
  min_memory_gb = 14
}

resource "databricks_job" "market_data_pipeline" {
  name = "Stonks_Maker_Daily_Ingestion"

  # 1. Ephemeral Job Cluster (Cost Optimization)
  job_cluster {
    job_cluster_key = "ingestion_cluster"
    new_cluster {
      spark_version      = "14.3.x-scala2.12"
      node_type_id       = data.databricks_node_type.available_node.id
      
      # 1. Set workers to 0 (Driver does all the work)
      num_workers        = 0
      
      # 2. Tell Spark to run locally on a single machine
      spark_conf = {
        "spark.databricks.cluster.profile" = "singleNode"
        "spark.master"                     = "local[*]"
      }
      
      # 3. Tell Databricks to provision this as a Single Node cluster
      custom_tags = {
        "ResourceClass" = "SingleNode"
      }

      data_security_mode = "SINGLE_USER"
    }
  }

  # 2. Task 1: OHLCV Ingestion
  task {
    task_key        = "ohlcv_ingestion"
    job_cluster_key = "ingestion_cluster"

    spark_python_task {
      # Dynamically maps to the Git repo synced in Step 4
      python_file = "${databricks_repo.stonks_maker_repo.workspace_path}/infrastructure/scripts/databricks_ohlcv_ingestion.py"
    }
  }

  # 3. Task 2: News Ingestion (Runs in parallel with OHLCV)
  task {
    task_key        = "news_ingestion"
    job_cluster_key = "ingestion_cluster"

    spark_python_task {
      python_file = "${databricks_repo.stonks_maker_repo.workspace_path}/infrastructure/scripts/databricks_news_ingestion.py"
    }

    # Dynamically installs external pip packages when the cluster boots
    library {
      pypi {
        package = "yfinance"
      }
    }
  }

  # 4. Schedule: 6:00 PM EST, Monday through Friday (Post-market close)
  schedule {
    quartz_cron_expression = "0 0 18 ? * MON-FRI"
    timezone_id            = "America/New_York"
  }
}