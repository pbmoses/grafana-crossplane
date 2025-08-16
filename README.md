# The following is the beginning of an "as code" approach to Observability utilizing [Crossplane](https://www.crossplane.io/) and [Grafana Cloud](https://grafana.com/products/cloud/)

*Disclaimer: The setup is for demonstration purposes and is not Grafana official documentation or configuration. It's a proof of concept. This was developed on an ultra low cost (< 160.00 USD) Raspberry Pi k3s cluster.* 

```
k get nodes -o wide
NAME        STATUS   ROLES                  AGE     VERSION        INTERNAL-IP    EXTERNAL-IP   OS-IMAGE                         KERNEL-VERSION      CONTAINER-RUNTIME
raspi64-0   Ready    control-plane,master   6d      v1.33.3+k3s1   192.168.0.31   <none>        Debian GNU/Linux 12 (bookworm)   6.6.62-v8+          containerd://2.0.5-k3s2
raspi64-1   Ready    <none>                 5d23h   v1.33.3+k3s1   192.168.0.32   <none>        Debian GNU/Linux 12 (bookworm)   6.6.20+rpt-rpi-v8   containerd://2.0.5-k3s2
raspi64-2   Ready    <none>                 4d19h   v1.33.3+k3s1   192.168.0.33   <none>        Debian GNU/Linux 12 (bookworm)   6.6.20+rpt-rpi-v8   containerd://2.0.5-k3s2
```

Observability as Code is the practice of defining, managing, and automating observability tools (like logging, metrics, traces, dashboards, and alerts) using code—typically version-controlled and automated through CI/CD pipelines—rather than manual setup. 

The following information is for demonstrative purposes, offering an entry point and is not a be-all-end-all for Observability as Code nor for Crossplane. 

It is assumed that you have a healthy Kubernetes cluster [Brief notes on Raspeberry pi +k3s](https://github.com/pbmoses/k3s-1) and some experience with Kubernetes. The manifests directory of this repo contains the needed manifests, they will also be demonstrated below. [ArgoCD](https://argo-cd.readthedocs.io/en/stable/) is the GitOps tooling that I normally utilize to manage provisioning, while there is some overlap, I see these tools as being complimentary to one another. 

Why Crossplane? 

Because it's enterprise ready and capable of managing most of what I need via Kubernetes manifests. It's platform engineering, not sys admin. 

## Installing Crossplane
`helm repo add crossplane-stable https://charts.crossplane.io/stable`

and

`helm repo update`

and finally:

`helm install crossplane --namespace crossplane-system --create-namespace crossplane-stable/crossplane`


## Creating the token in Grafana Cloud

<img width="633" height="515" alt="Screenshot 2025-08-16 at 2 32 26 PM" src="https://github.com/user-attachments/assets/f0112224-4fe7-405c-a353-8bffe2511017" />

## Creating the secret

A secret is required to configure access to the external resources, in this case Grafana Cloud. Ideally, a secrets manager along with something similar to the External Secrets Operator should be utilized to protect sensitive data. For the demo, we will use a standard Kubernetes secret. The auth is the token that was created in the previous step. 


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
      "url": "<your slug>.grafana.net:'
      "auth": "<token>"
    }
```


## Creating the Provider
[Providers](https://docs.crossplane.io/latest/packages/providers/#install-a-provider) in Crossplane allow us to Provision infrastructure and services. Providers are controllers that understand how to manage resources in external systems. Declarative approaches are utilized via Kubernetes manifests, you will declare the state and Kubernetes will reconcile to meet the declaration. 

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

Check your CRDs:

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

## Creating the providerConfig

Provider Configs are Custom Resources in Kubernetes that allow the provider to interact with the API. In this case, `crossplane-provider-grafana` and the `Grafana Cloud` API(s).

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

The following is an example of a foldr creation in Grafana Cloud. 

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

The Following is an example of a dashboard in Grafana Cloud. 

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


# Parsing JSON API output

The `parsers` directory contains multiple Python parsers that will take a JSON input file and output the appropriate Kubernetes manifests.  

Various APIs can be utilized to interact with Grafana Cloud, that output can be parsed and Crossplane compatible manifests. Initial thoughts are to approach this in the following manner:
![crossplane_flow_with_api](https://github.com/user-attachments/assets/e8dd0c35-d4f3-414a-83c8-d8af87ff7c6c)
<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="400">
<rect x="20" y="120" width="120" height="60" rx="10" ry="10" fill="#ffe6cc" stroke="#d79b00"/>
<text x="80" y="150" font-size="12" text-anchor="middle" fill="#000">query API</text>

<rect x="180" y="120" width="120" height="60" rx="10" ry="10" fill="#dae8fc" stroke="#6c8ebf"/>
<text x="240" y="150" font-size="12" text-anchor="middle" fill="#000">input.json</text>
<text x="240" y="165" font-size="10" text-anchor="middle" fill="#000">(JSON schema)</text>

<rect x="340" y="120" width="180" height="60" rx="10" ry="10" fill="#dae8fc" stroke="#6c8ebf"/>
<text x="430" y="150" font-size="12" text-anchor="middle" fill="#000">Python Parser</text>
<text x="430" y="165" font-size="10" text-anchor="middle" fill="#000">(generate_crossplane_manifests.py)</text>

<rect x="560" y="120" width="180" height="60" rx="10" ry="10" fill="#dae8fc" stroke="#6c8ebf"/>
<text x="650" y="150" font-size="12" text-anchor="middle" fill="#000">YAML Templates</text>
<text x="650" y="165" font-size="10" text-anchor="middle" fill="#000">(Composition, ProviderConfig)</text>

<rect x="780" y="120" width="140" height="60" rx="10" ry="10" fill="#dae8fc" stroke="#6c8ebf"/>
<text x="850" y="150" font-size="12" text-anchor="middle" fill="#000">output/</text>
<text x="850" y="165" font-size="10" text-anchor="middle" fill="#000">(manifests/*.yaml)</text>

<rect x="440" y="250" width="200" height="60" rx="10" ry="10" fill="#dae8fc" stroke="#6c8ebf"/>
<text x="540" y="275" font-size="12" text-anchor="middle" fill="#000">kubectl apply -f output/</text>
<text x="540" y="290" font-size="10" text-anchor="middle" fill="#000">(optional)</text>

<rect x="700" y="250" width="180" height="60" rx="10" ry="10" fill="#dae8fc" stroke="#6c8ebf"/>
<text x="790" y="275" font-size="12" text-anchor="middle" fill="#000">Kubernetes</text>
<text x="790" y="290" font-size="10" text-anchor="middle" fill="#000">(Crossplane)</text>

<rect x="920" y="250" width="120" height="60" rx="10" ry="10" fill="#dae8fc" stroke="#6c8ebf"/>
<text x="980" y="285" font-size="12" text-anchor="middle" fill="#000">Grafana Cloud</text>

<!-- Arrows -->
<line x1="140" y1="150" x2="180" y2="150" stroke="#000" marker-end="url(#arrow)" />
<line x1="300" y1="150" x2="340" y2="150" stroke="#000" marker-end="url(#arrow)" />
<line x1="520" y1="150" x2="560" y2="150" stroke="#000" marker-end="url(#arrow)" />
<line x1="740" y1="150" x2="780" y2="150" stroke="#000" marker-end="url(#arrow)" />
<line x1="850" y1="180" x2="540" y2="250" stroke="#000" marker-end="url(#arrow)" />
<line x1="640" y1="280" x2="700" y2="280" stroke="#000" marker-end="url(#arrow)" />
<line x1="880" y1="280" x2="920" y2="280" stroke="#000" marker-end="url(#arrow)" />

<defs>
<marker id="arrow" markerWidth="10" markerHeight="10" refX="10" refY="3" orient="auto" markerUnits="strokeWidth">
  <path d="M0,0 L0,6 L9,3 z" fill="#000" />
</marker>
</defs>
</svg>


# Interacting with APIs

Utilizing the Grafana Cloud APIs is fairly straight forward, considering you have the correct token and endpoint.

`curl -H "Authorization: Bearer "<token>" -H "Content-Type: application/json" https://<SLUG>.grafana.net/api/folders| jq .`

A successful query to the folders enpoint should return data similar to the following, which can be redirected to a file with common *nix tools. The resulting file will be the input file for the Python parser:  `curl -H "Authorization: Bearer "<token>" -H "Content-Type: application/json" https://<SLUG>.grafana.net/api/folders| jq . > folders.json`:

```
[
  {
    "id": 108,
    "uid": "feui7sfwdd0cgc",
    "title": "Crossplane Demo Folder"
  },
  {
    "id": 66,
    "uid": "bdpkwahk6emm8e",
    "title": "declarative-grafana"
  },
  {
    "id": 2,
    "uid": "fdjqenyj148aof",
    "title": "GrafanaCloud"
  },
  {
    "id": 81,
    "uid": "integration---linux-node",
    "title": "Integration - Linux Node"
  },
  {
    "id": 68,
    "uid": "integration---macos-node",
    "title": "Integration - MacOS Node"
  },
  {
    "id": 75,
    "uid": "integration---microsoft-sql-server",
    "title": "Integration - Microsoft SQL Server"
  },
  {
    "id": 44,
    "uid": "grafana-demodashboards-weather",
    "title": "⛅ Grafana Weather Demo Dashboards"
  }
]
```

*The `parsers` directory contains multiple Python parsers that will take a JSON input file and output the appropriate Kubernetes manifests.*

