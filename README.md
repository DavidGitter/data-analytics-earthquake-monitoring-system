# Data-Analytics-Earthquake-Monitoring-System

***

## Table of Contents

1. [Contributors](#contributors)
2. [About](#about)
3. [Architecture](#architecture)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Test](#test)

***

## Contributors
#### Owner
- Silas Jung
- evoila GmbH

***

## About
This repo contains a basic on-premise cloud native lakehouse extended with the purpose for monitoring earthquake data. All softwares used are open-source.

***

## Architecture
![Architecture Image](https://github.com/DavidGitter/data-analytics-earthquake-monitoring-system/blob/820f19f19dbe005e6bb35ebced265b1457ded245/docs/diagrams/architecture/architecture.jpg?raw=true)

***

## Installation
The monitoring system is packaged as a [helm chart](https://helm.sh/). For installation, a deployment with [ArgoCD](https://argo-cd.readthedocs.io/en/stable/) is provided. To deploy the chart as [ArgoCD application](https://argo-cd.readthedocs.io/en/stable/operator-manual/declarative-setup/) the following steps are taken:

#### 1. Setup ArgoCD
* Create the "argocd" namespace
````
kubectl create namespace argocd
````

* Install the ArgoCD Server and CRDs for ArgoCD on the cluster
````
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
````

#### 2. Deploy the application
* Apply the **"argocd-starter.yaml"** found in the "src"-folder of this repository
````
kubectl apply -f https://raw.githubusercontent.com/DavidGitter/data-analytics-earthquake-monitoring-system/main/src/argocd-starter.yaml -n argocd
````

> **_NOTE:_**  Another way to install the system is manually with the standalone helm chart in /src/eqms or through the web UI of ArgoCD. For more information on this, please visit https://helm.sh/ and https://argo-cd.readthedocs.io/en/stable/.

#### 3. Observe the deployment
* Portforward the Web-UI of the ArgoCD Server on your cluster
````
kubectl port-forward svc/argocd-server -n argocd 8080:443
````

* Login as user "admin" using the initial admin password found at the **"argocd-initial-admin-secret"** secret in the ArgoCD namespace

* If everything works correctly the deployment is visible after some time in the UI-Dashboard as **"healthy"**

***

## Usage

#### 1. Access UIs
* *Show the external adresses of Nifi, MinIO and Superset using the following command*
````
kubectl get svc --all-namespaces
````
* To access the UI for a specific service, enter the adress gathered from the above command with the port of it in your browser with the format: http://ext-adress-of-service:port

> **_NOTE:_**  Due to a bug in the image (as of 09/10/23), access to the Superset interface needs to be done through port forwarding.

#### 2. Workflow
The system will automaticly pull an earthquake event from the [USGS-API](https://earthquake.usgs.gov/fdsnws/event/1/) once every full hour from the start of the application.

> **_NOTE:_**  The superset dashboard diagrams throw errors aslong as there is no data available. To instantly fetch data from the api the user can start-stop the test processor in the nifi ui located in the api_usgs subflow.

***

## Test
By setting the `eqms.useTestData` in the values of the eqms-chart to `true` the init-minio job loads a collection of old earthquake data in the minio bucket. This can be used to quickly test or showcase the system.
