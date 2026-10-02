variable "project_name" {
  type = string
}

variable "git_url" {
  description = "URL of the Git repository"
  type        = string
}

variable "git_branch" {
  description = "current working branch"
  type        = string
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