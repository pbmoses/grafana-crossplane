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

