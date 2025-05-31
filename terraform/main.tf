# Notebook Environment
resource "google_notebooks_environment" "environment" {
  name = "notebooks-environment"
  location = "us-west1-a"  
}

# Tensorboard for Monitoring
resource "google_vertex_ai_tensorboard" "default" {
  display_name = "vertex-ai-tensorboard-sample-name"
  region       = "us-central1"
}

