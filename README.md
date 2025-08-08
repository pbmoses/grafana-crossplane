# The following is the beginning of an "as code" approach to Observability utilizing [Crossplane](https://www.crossplane.io/) and [Grafana Cloud](https://grafana.com/products/cloud/)

Observability as Code is the practice of defining, managing, and automating observability tools (like logging, metrics, traces, dashboards, and alerts) using code—typically version-controlled and automated through CI/CD pipelines—rather than manual setup. 

The following information is for demonstrative purposes, offering an entry point and is not a be-all-end-all for Observability as Code nor for Crossplane. 

It is assumed that you have a healthy Kubernetes cluster and some experience with Kubernetes. The manifests directory of this repo contains the needed manifests, they will also be demonstrated below. [ArgoCD](https://argo-cd.readthedocs.io/en/stable/) is the GitOps tooling that I normally utilize to manage provisioning, while there is some overlap, I see these tools as being complimentary to one another. 

## Installing Crossplane
`helm repo add crossplane-stable https://charts.crossplane.io/stable`

and

`helm repo update`

Validate:
```
raspi64-0:~#  kubectl get crds | grep grafana | grep crossplane
accesspolicies.cloud.grafana.crossplane.io                          2025-08-07T00:02:07Z
accesspolicytokens.cloud.grafana.crossplane.io                      2025-08-07T00:02:07Z
alerts.ml.grafana.crossplane.io                                     2025-08-07T00:02:08Z
annotations.oss.grafana.crossplane.io                               2025-08-07T00:02:08Z
apps.frontendobservability.grafana.crossplane.io                    2025-08-07T00:02:08Z
awsaccounts.cloudprovider.grafana.crossplane.io                     2025-08-07T00:02:07Z
awscloudwatchscrapejobs.cloudprovider.grafana.crossplane.io         2025-08-07T00:02:07Z
awsresourcemetadatascrapejobs.cloudprovider.grafana.crossplane.io   2025-08-07T00:02:07Z
azurecredentials.cloudprovider.grafana.crossplane.io                2025-08-07T00:02:07Z
checkalerts.sm.grafana.crossplane.io                                2025-08-07T00:02:09Z
checks.sm.grafana.crossplane.io                                     2025-08-07T00:02:10Z
collectors.fleetmanagement.grafana.crossplane.io                    2025-08-07T00:02:07Z
contactpoints.alerting.grafana.crossplane.io                        2025-08-07T00:02:07Z
dashboardpermissionitems.oss.grafana.crossplane.io                  2025-08-07T00:02:08Z
dashboardpermissions.oss.grafana.crossplane.io                      2025-08-07T00:02:09Z
dashboardpublics.oss.grafana.crossplane.io                          2025-08-07T00:02:08Z
dashboards.oss.grafana.crossplane.io                                2025-08-07T00:02:09Z
datasourceconfiglbacrules.enterprise.grafana.crossplane.io          2025-08-07T00:02:07Z
datasourceconfigs.oss.grafana.crossplane.io                         2025-08-07T00:02:09Z
datasourcepermissionitems.enterprise.grafana.crossplane.io          2025-08-07T00:02:07Z
datasourcepermissions.enterprise.grafana.crossplane.io              2025-08-07T00:02:07Z
datasources.oss.grafana.crossplane.io                               2025-08-07T00:02:09Z
escalationchains.oncall.grafana.crossplane.io                       2025-08-07T00:02:08Z
escalations.oncall.grafana.crossplane.io                            2025-08-07T00:02:08Z
```


## Creating the secret

A secret is required to configure access to the external resources, in this case Grafana Cloud. Ideally, a secrets manager and something similar to the External Secrets Operator should be utilized to protect sensitive data. For the demo, we will use a standard Kubernetes secret. 


``` bash
apiVersion: v1
kind: Secret
metadata:
  name: grafana-credentials
  namespace: crossplane-system
type: Opaque

##please don't put sensitive info in git use a secrets manager, this is just for demo purposes. 
stringData:
  credentials: |
    {
      "url": "your grafana URL:'
      "auth": "g.........."
    }
```


## Creating the Provider
[Providers](https://docs.crossplane.io/latest/concepts/providers/) in Crossplane allow us to Provision infrastructure and services. Providers are controllers that understand how to manage resources in external systems. Declarative approaches are utilized via Kubernetes manifests, you will declare the state and Kubernetes will reconcile to meet the declaration. 

For the following demo, the [Grafana Crosplane Provider](https://github.com/grafana/crossplane-provider-grafana) is utilized. 

```
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-grafana
spec:
  package: xpkg.upbound.io/grafana/provider-grafana:v0.30.0
```

## Creating the providerConfig

```
kind: ProviderConfig
metadata:
  name: grafana-provider
  namespace: crossplane-system
spec:
  credentials:
    source: Secret
    secretRef:
      namespace: crossplane-system
      name: grafana-credentials
      key: credentials
  endpoint: https://<SLUG>.grafana.net
  ```
## Creating folders
```
kind: Folder
metadata:
  name: crossplane-created-demo-folder
spec:
  providerConfigRef:
    name: grafana-provider
  forProvider:
    title: Crossplane Demo Folder
```
## Creating dashboards
```
apiVersion: oss.grafana.crossplane.io/v1alpha1
kind: Dashboard
metadata:
  name: crossplane-example-dashboard
  namespace: crossplane-system
spec:
  forProvider:
    configJson: |
      {
        "title": "Crossplane Example Dashboard",
        "uid": "example-dashboard",
        "panels": [
          {
            "type": "text",
            "title": "Hello from Crossplane",
            "gridPos": { "x": 0, "y": 0, "w": 24, "h": 4 },
            "options": {
              "content": "This dashboard was provisioned using Crossplane!",
              "mode": "markdown"
            }
          }
        ]
      }
  providerConfigRef:
    name: grafana-provider
```

<img width="1031" height="288" alt="Screenshot 2025-08-08 at 1 57 24 PM" src="https://github.com/user-attachments/assets/391042fa-f782-4ded-bfa2-e743016ca0aa" />





