# The following is the beginning of an "as code" approach to Observability utilizing [Crossplane](https://www.crossplane.io/) and [Grafana Cloud](https://grafana.com/products/cloud/)

*Disclaimer: The setup is for demonstration purposes and is not Grafana official documentation or configuration. It's a proof of concept.* 

Observability as Code is the practice of defining, managing, and automating observability tools (like logging, metrics, traces, dashboards, and alerts) using code—typically version-controlled and automated through CI/CD pipelines—rather than manual setup. 

The following information is for demonstrative purposes, offering an entry point and is not a be-all-end-all for Observability as Code nor for Crossplane. 

It is assumed that you have a healthy Kubernetes cluster and some experience with Kubernetes. The manifests directory of this repo contains the needed manifests, they will also be demonstrated below. [ArgoCD](https://argo-cd.readthedocs.io/en/stable/) is the GitOps tooling that I normally utilize to manage provisioning, while there is some overlap, I see these tools as being complimentary to one another. 

Why Crossplane? 

Because it's enterprise ready and capable of managing most of what I need via Kubernetes manifests. It's platform engineering, not sys admin. 

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

A secret is required to configure access to the external resources, in this case Grafana Cloud. Ideally, a secrets manager along with something similar to the External Secrets Operator should be utilized to protect sensitive data. For the demo, we will use a standard Kubernetes secret. 


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
Validate:

```
k describe providers provider-grafana
Name:         provider-grafana
Namespace:    
Labels:       <none>
Annotations:  <none>
API Version:  pkg.crossplane.io/v1
Kind:         Provider
Metadata:
  Creation Timestamp:  2025-08-07T00:01:56Z
  Generation:          1
  Resource Version:    371903
  UID:                 a6d10e2b-f40f-4cc3-8088-45d5cea4ed6b
Spec:
  Ignore Crossplane Constraints:  false
  Package:                        xpkg.upbound.io/grafana/provider-grafana:v0.30.0
  Package Pull Policy:            IfNotPresent
  Revision Activation Policy:     Automatic
  Revision History Limit:         1
  Runtime Config Ref:
    API Version:               pkg.crossplane.io/v1beta1
    Kind:                      DeploymentRuntimeConfig
    Name:                      default
  Skip Dependency Resolution:  false
Status:
  Conditions:
    Last Transition Time:  2025-08-07T00:06:23Z
    Reason:                HealthyPackageRevision
    Status:                True
    Type:                  Healthy
    Last Transition Time:  2025-08-07T00:01:56Z
    Reason:                ActivePackageRevision
    Status:                True
    Type:                  Installed
  Current Identifier:      xpkg.upbound.io/grafana/provider-grafana:v0.30.0
  Current Revision:        provider-grafana-3adbcd288f8f
  Resolved Package:        xpkg.upbound.io/grafana/provider-grafana:v0.30.0
Events:                    <none>
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

Validate:

```
 k describe providerConfig grafana-provider
Name:         grafana-provider
Namespace:    
Labels:       <none>
Annotations:  <none>
API Version:  grafana.crossplane.io/v1beta1
Kind:         ProviderConfig
Metadata:
  Creation Timestamp:  2025-08-07T19:22:20Z
  Finalizers:
    in-use.crossplane.io
  Generation:        5
  Resource Version:  695277
  UID:               796d9eb2-2086-471a-a873-06a900e5de33
Spec:
  Credentials:
    Secret Ref:
      Key:        credentials
      Name:       grafana-credentials
      Namespace:  crossplane-system
    Source:       Secret
Status:
  Conditions:
    Last Transition Time:  2025-08-07T19:47:57Z
    Reason:                Available
    Status:                True
    Type:                  Ready
  Users:                   3
Events:                    <none>
```

## Creating folders
```
apiVersion: oss.grafana.crossplane.io/v1alpha1
kind: Folder
metadata:
  name: crossplane-demo
  labels:
    demo.philmoses.com/example-name: crossplane-demo
spec:
  providerConfigRef:
    name: grafana-provider
  forProvider:
    title: Crossplane Demo Folder
```

Validate:

```
 k describe folder crossplane-demo
Name:         crossplane-demo
Namespace:    
Labels:       demo.philmoses.com/example-name=crossplane-demo
Annotations:  crossplane.io/external-create-pending: 2025-08-08T20:56:48Z
              crossplane.io/external-create-succeeded: 2025-08-08T20:56:49Z
              crossplane.io/external-name: 0:beuf411emt5oga
API Version:  oss.grafana.crossplane.io/v1alpha1
Kind:         Folder
Metadata:
  Creation Timestamp:  2025-08-08T20:56:48Z
  Finalizers:
    finalizer.managedresource.crossplane.io
  Generation:        3
  Resource Version:  693741
  UID:               940bd3b3-3ac2-49dc-85eb-212cab3a4052
Spec:
  Deletion Policy:  Delete
  For Provider:
    Org Id:  0
    Title:   Crossplane Demo Folder
    UID:     beuf411emt5oga
  Init Provider:
  Management Policies:
    *
  Provider Config Ref:
    Name:  grafana-provider
Status:
  At Provider:
    Id:                            0:beuf411emt5oga
    Org Id:                        0
    Parent Folder UID:             
    Prevent Destroy If Not Empty:  false
    Title:                         Crossplane Demo Folder
    UID:                           beuf411emt5oga
    URL:                           https://pbmoses.grafana.net/dashboards/f/beuf411emt5oga/crossplane-demo-folder
  Conditions:
    Last Transition Time:  2025-08-08T20:56:50Z
    Reason:                Available
    Status:                True
    Type:                  Ready
    Last Transition Time:  2025-08-08T20:56:49Z
    Reason:                ReconcileSuccess
    Status:                True
    Type:                  Synced
Events:
  Type     Reason                       Age   From                                                     Message
  ----     ------                       ----  ----                                                     -------
  Normal   CreatedExternalResource      16m   managed/oss.grafana.crossplane.io/v1alpha1, kind=folder  Successfully requested creation of external resource
```

## Creating dashboards

```
apiVersion: oss.grafana.crossplane.io/v1alpha1
kind: Dashboard
metadata:
  name: example-dashboard
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
            "title": "Goodbye from Crossplane",
            "gridPos": { "x": 0, "y": 0, "w": 24, "h": 4 },
            "options": {
              "content": "This dashboard was provisioned using Crossplane!",
              "mode": "markdown"
            }
          }
        ]
      }
    folderSelector:
      matchLabels:
        demo.philmoses.com/example-name: crossplane-demo 
  providerConfigRef:
    name: grafana-provider
```

Validate:

```
 k describe dashboard example-dashboard
Name:         example-dashboard
Namespace:    
Labels:       <none>
Annotations:  crossplane.io/external-create-pending: 2025-08-08T20:57:06Z
              crossplane.io/external-create-succeeded: 2025-08-08T20:57:06Z
              crossplane.io/external-name: 0:example-dashboard
API Version:  oss.grafana.crossplane.io/v1alpha1
Kind:         Dashboard
Metadata:
  Creation Timestamp:  2025-08-08T20:57:06Z
  Finalizers:
    finalizer.managedresource.crossplane.io
  Generation:        4
  Resource Version:  693785
  UID:               113f4ebb-196b-4a13-b37e-bb9ed9b615bc
Spec:
  Deletion Policy:  Delete
  For Provider:
    Config Json:  {
  "title": "Crossplane Example Dashboard",
  "uid": "example-dashboard",
  "panels": [
    {
      "type": "text",
      "title": "Goodbye from Crossplane",
      "gridPos": { "x": 0, "y": 0, "w": 24, "h": 4 },
      "options": {
        "content": "This dashboard was provisioned using Crossplane!",
        "mode": "markdown"
      }
    }
  ]
}

    Folder:  beuf411emt5oga
    Folder Ref:
      Name:  crossplane-demo
    Folder Selector:
      Match Labels:
        demo.philmoses.com/example-name:  crossplane-demo
    Org Id:                               0
  Init Provider:
  Management Policies:
    *
  Provider Config Ref:
    Name:  grafana-provider
Status:
  At Provider:
    Config Json:   {"panels":[{"gridPos":{"h":4,"w":24,"x":0,"y":0},"options":{"content":"This dashboard was provisioned using Crossplane!","mode":"markdown"},"title":"Goodbye from Crossplane","type":"text"}],"title":"Crossplane Example Dashboard","uid":"example-dashboard"}
    Dashboard Id:  98
    Folder:        beuf411emt5oga
    Id:            0:example-dashboard
    Org Id:        0
    UID:           example-dashboard
    URL:           https://pbmoses.grafana.net/d/example-dashboard/crossplane-example-dashboard
    Version:       1
  Conditions:
    Last Transition Time:  2025-08-08T20:57:08Z
    Reason:                Available
    Status:                True
    Type:                  Ready
    Last Transition Time:  2025-08-08T20:57:06Z
    Reason:                ReconcileSuccess
    Status:                True
    Type:                  Synced
Events:
  Type     Reason                       Age   From                                                        Message
  ----     ------                       ----  ----                                                        -------
  Normal   CreatedExternalResource      17m   managed/oss.grafana.crossplane.io/v1alpha1, kind=dashboard  Successfully requested creation of external resource
```


<img width="1031" height="288" alt="Screenshot 2025-08-08 at 1 57 24 PM" src="https://github.com/user-attachments/assets/391042fa-f782-4ded-bfa2-e743016ca0aa" />





