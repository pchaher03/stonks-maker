variable "project_name" {
  type = string
}

variable "resource_group_name" {
    type = string
}

variable "resource_group_location" {
    type = string
}

variable "access_connector_id" {
    type = string
}

variable "key_vault_id" {
  description = "The ID of the Azure Key Vault"
  type        = string
}

variable "key_vault_uri" {
  description = "The URI of the Azure Key Vault"
  type        = string
}

variable "git_url" {
  description = "URL of the Git repository"
  type        = string
}

variable "git_branch" {
  description = "current working branch"
  type        = string
}