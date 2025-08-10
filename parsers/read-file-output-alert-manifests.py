import json
import yaml
import os
import re

# Utility to sanitize folder titles for Kubernetes metadata.name
def sanitize_name(title):
    name = title.lower()
    name = re.sub(r'[^a-z0-9]+', '-', name)
    name = name.strip('-')
    return name[:63]  # K8s name length limit

# Load JSON input from file
input_file = "alerts.json"
with open(input_file, "r") as f:
    alerts_json = json.load(f)

# Output directory for YAML manifests
output_dir = "manifests/alerts"
os.makedirs(output_dir, exist_ok=True)

# Generate and save YAML files
for alert in alerts_json:
    safe_name = sanitize_name(alert['title'])
    file_name = f"{safe_name}.yaml"
    file_path = os.path.join(output_dir, file_name)

    manifest = {
        "apiVersion": "oss.grafana.crossplane.io/v1alpha1",
        "kind": "Alert",
        "metadata": {
            "name": safe_name,
            "labels": {
                "demo.philmoses.com/example-name": "crossplane-demo"
            }
        },
        "spec": {
            "forProvider": {
                "title": alert["title"]
            },
            "providerConfigRef": {
                "name": "grafana-provider"
            },
            "deletionPolicy": "Delete"
        }
    }

    with open(file_path, 'w') as f:
        yaml.dump(manifest, f, sort_keys=False)

    print(f"Generated: {file_path}")
