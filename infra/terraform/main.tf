variable "github_owner" {}
variable "repo" { default = "vision-model-benchmark-cloud" }

terraform {
  required_providers {
    github = { source = "integrations/github" }
    neon   = { source = "neondatabase/neon" }
  }
}

provider "github" {
  owner = var.github_owner
}

resource "neon_project" "bench" {
  name = "vision-benchmark"
}

resource "github_actions_variable" "pages_url" {
  repository    = var.repo
  variable_name = "PAGES_URL"
  value         = "https://${var.github_owner}.github.io/${var.repo}/"
}
