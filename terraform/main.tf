provider "google" {
  project     = var.project_id
  region      = var.region
  zone        = var.zone
}

# Notebook Environment
resource "google_notebooks_environment" "environment" {
  name = "notebooks-environment"
  location = "us-east1"  
}

# Tensorboard for Monitoring
resource "google_vertex_ai_tensorboard" "default" {
  display_name = "vertex-ai-tensorboard-sample-name"
  region       = "us-east1"
}

