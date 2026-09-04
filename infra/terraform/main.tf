variable "github_owner" {}
variable "repo" { default = "vision-model-benchmark-cloud" }

# Paste your Neon Organization ID here
variable "neon_org_id" {
  default = "org-fancy-surf-33732413"
}

terraform {
  required_providers {
    github = { source = "integrations/github" }
    neon   = { source = "kislerdm/neon" }
  }
}

provider "github" {
  owner = var.github_owner
}

provider "neon" {}

resource "neon_project" "bench" {
  name   = "vision-benchmark"
  org_id = var.neon_org_id
}

resource "github_actions_variable" "pages_url" {
  repository    = var.repo
  variable_name = "PAGES_URL"
  value         = "https://${var.github_owner}.github.io/${var.repo}/"
}
