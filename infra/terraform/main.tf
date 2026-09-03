terraform {
  required_providers {
    cloudflare = { source = "cloudflare/cloudflare" }
    neon       = { source = "neondatabase/neon" }
    github     = { source = "integrations/github" }
  }
}

resource "cloudflare_r2_bucket" "artifacts" {
  account_id = var.cloudflare_account_id
  name       = "vision-bench-artifacts"
}

resource "neon_project" "bench" {
  name = "vision-bench"
}

resource "github_actions_variable" "r2_public_url" {
  repository    = var.repo_name
  variable_name = "R2_PUBLIC_URL"
  value         = var.r2_public_url
}
