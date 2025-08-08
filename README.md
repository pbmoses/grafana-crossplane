# The following is the beginning of an "as code" approach to Observability utilizing [Crossplane](https://www.crossplane.io/) and [Grafana Cloud](https://grafana.com/products/cloud/)

Observability as Code is the practice of defining, managing, and automating observability tools (like logging, metrics, traces, dashboards, and alerts) using code—typically version-controlled and automated through CI/CD pipelines—rather than manual setup. 

The following information is for demonstrative purposes, offering an entry point and is not a be-all-end-all for Observability as Code nor for Crossplane. 

It is assumed that you have a healthy Kubernetes cluster. If you do not, options available as `kind` 

## Installing Crossplane
`helm repo add crossplane-stable https://charts.crossplane.io/stable`
and
`helm repo update`

## Creating the Provider
[Providers](https://docs.crossplane.io/latest/concepts/providers/) in Crossplane allow us to Provision infrastructure and services. Providers are controllers that understand how to manage resources in external systems. Declarative approaches are utilized via Kubernetes manifests, you will declare the state and Kubernetes will reconcile to meet the declaration. 

For the following demo, the [Grafana Crosplane Provider](https://github.com/grafana/crossplane-provider-grafana) is utilized. 

## Creating the providerConfig

## Creating folders

## Creating dashboards


``` bash
k create -f cp.yaml
```


validate 
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

