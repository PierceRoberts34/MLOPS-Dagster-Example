provider "google" {
  project     = var.project_id
  region      = var.region
}

# Jenkins on Google Kubernetes Engine
resource "google_container_cluster" "jenkins_cd" {
  name     = "jenkins-cd"
  location = var.region

  initial_node_count = 2

  node_config {
    machine_type = "e2-standard-2"

    oauth_scopes = [
      "https://www.googleapis.com/auth/source.read_write",
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}
