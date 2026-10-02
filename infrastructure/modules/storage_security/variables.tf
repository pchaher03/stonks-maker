variable "project_name" {
  type = string
}

variable "resource_group_name" {
    type = string
}

variable "resource_group_location" {
    type = string
}


variable "alpha_vantage_api_key" {
  description = "API Key for Alpha Vantage"
  type        = string
  sensitive   = true
}

variable "news_api_key" {
  description = "API Key for NewsAPI"
  type        = string
  sensitive   = true
}