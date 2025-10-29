## 📚 Complete Assignment Template: Online Book Store

### I. Project Structure (Local Machine)

You will need to create the following directories and files to organize the submission.

```
/bookstore-microservices
├── user-service/                   <-- Service 1: Python/Flask
│   ├── app.py                      
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .gitignore
├── catalog-service/                <-- Service 2: Node.js/Express
│   ├── server.js                   
│   ├── package.json
│   ├── Dockerfile
│   └── .gitignore
└── kubernetes-manifests/           <-- Deployment Files
    ├── user-db-deployment.yaml     
    ├── user-service.yaml           
    ├── catalog-db-deployment.yaml  
    └── catalog-service.yaml        
```

-----

### II. Part 1: Design and Architecture

#### A. Application and Services Identified

The application is an **Online Book Store**. The core functions are mapped to the following services:

| Business Capability | Microservice | Implementation Status |
| :--- | :--- | :--- |
| **User/Account Management** | **User Service** | Implemented |
| **Catalog Browsing & Search** | **Catalog Service** | Implemented |
| Order Management | Order Service | Planned |
| Shopping Cart | Cart Service | Planned |

#### B. System Operations (Commands and Queries)

| Service | Operation Type | Operation | Collaboration |
| :--- | :--- | :--- | :--- |
| **User Service** | Command | `POST /users` (Register User) | None |
| | Query | `GET /users/{id}` (Get User Details) | None |
| **Catalog Service** | Command | `POST /books` (Add New Book) | None |
| | Query | `GET /books/{id}` (Get Book Details) | None |

-----

### III. Part 2: Code Base and Dockerfiles

#### A. User Service (Python/Flask)

**1. `user-service/requirements.txt`**

```txt
Flask
psycopg2-binary
```

**2. `user-service/app.py`**

```python
import os
from flask import Flask, jsonify, request

app = Flask(__name__)

# Mock database
USERS = {
    "1": {"username": "alice", "email": "alice@example.com", "role": "customer"},
    "2": {"username": "bob_admin", "email": "bob@admin.com", "role": "admin"}
}

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "UP", "db_status": "ok"})

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    user = USERS.get(user_id)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    new_id = str(len(USERS) + 1)
    USERS[new_id] = data
    return jsonify({"id": new_id, "message": "User created"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

**3. `user-service/Dockerfile`**

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

#### B. Catalog Service (Node.js/Express)

**1. `catalog-service/package.json`**

```json
{
  "name": "catalog-service",
  "version": "1.0.0",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  }
}
```

**2. `catalog-service/server.js`**

```javascript
const express = require('express');
const app = express();
const port = 3000;

app.use(express.json());

// Mock catalog data
const BOOKS = [
    { id: "101", title: "Microservices Explained", author: "G. Engineer", price: 49.99 },
    { id: "102", title: "Kubernetes Basics", author: "A. Developer", price: 35.50 }
];

app.get('/health', (req, res) => {
    res.json({ status: "UP", db_status: "ok" });
});

app.get('/books', (req, res) => {
    res.json(BOOKS);
});

app.get('/books/:id', (req, res) => {
    const book = BOOKS.find(b => b.id === req.params.id);
    if (book) {
        return res.json(book);
    }
    res.status(404).json({ error: "Book not found" });
});

app.listen(port, () => {
    console.log(`Catalog Service listening at http://localhost:${port}`);
});
```

**3. `catalog-service/Dockerfile`**

```dockerfile
FROM node:20-alpine
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD [ "node", "server.js" ]
```

-----

### IV. Part 3: Deployment Manifests and Steps

These YAML files configure the databases and services on the Minikube cluster.

#### A. Database Deployment YAMLs

**1. `kubernetes-manifests/user-db-deployment.yaml`** (PostgreSQL)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-db-deployment
  labels:
    app: user-db
spec:
  replicas: 1
  selector:
    matchLabels:
      app: user-db
  template:
    metadata:
      labels:
        app: user-db
    spec:
      containers:
      - name: user-db
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: "userdb"
        - name: POSTGRES_USER
          value: "user"
        - name: POSTGRES_PASSWORD
          value: "pass"
---
apiVersion: v1
kind: Service
metadata:
  name: user-db-service
spec:
  selector:
    app: user-db
  ports:
    - protocol: TCP
      port: 5432
      targetPort: 5432
  type: ClusterIP
```

**2. `kubernetes-manifests/catalog-db-deployment.yaml`** (MongoDB - Conceptual, same structure as above using `mongo` image and port `27017`)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: catalog-db-deployment
  labels:
    app: catalog-db
spec:
  replicas: 1
  selector:
    matchLabels:
      app: catalog-db
  template:
    metadata:
      labels:
        app: catalog-db
    spec:
      containers:
      - name: catalog-db-container
        image: mongo:5.0-focal # Using a versioned MongoDB image
        ports:
        - containerPort: 27017
        env: # Environment variables for initial database setup
        - name: MONGO_INITDB_DATABASE
          value: "catalogdb"
        - name: MONGO_INITDB_ROOT_USERNAME
          value: "cataloguser"
        - name: MONGO_INITDB_ROOT_PASSWORD
          value: "catalogpass"
        # Persistence configuration would typically go here
---
# 2. Service to expose the Catalog DB internally
apiVersion: v1
kind: Service
metadata:
  name: catalog-db-service # Internal DNS name used by the Catalog Microservice
spec:
  selector:
    app: catalog-db
  ports:
    - protocol: TCP
      port: 27017
      targetPort: 27017
  type: ClusterIP # Internal-only access
```


#### B. Microservice Deployment YAMLs

**1. `kubernetes-manifests/user-service.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-deployment
  labels:
    app: user-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-container
        image: user-service:v1
        imagePullPolicy: Never # Use local image
        ports:
        - containerPort: 5000
        env:
        - name: DB_HOST
          value: "user-db-service"
---
apiVersion: v1
kind: Service
metadata:
  name: user-service
spec:
  selector:
    app: user-service
  ports:
    - protocol: TCP
      port: 8080 # External Port
      targetPort: 5000 # Container Port
  type: NodePort # Allows external access
```

**2. `kubernetes-manifests/catalog-service.yaml`** (Conceptual, same structure as above using `catalog-service:v1` image, container port `3000`, and external port `8081`.

```yaml
# 1. Deployment for the Catalog Service
apiVersion: apps/v1
kind: Deployment
metadata:
  name: catalog-deployment
  labels:
    app: catalog-service
spec:
  replicas: 2 # Scalability: Run 2 instances
  selector:
    matchLabels:
      app: catalog-service
  template:
    metadata:
      labels:
        app: catalog-service
    spec:
      containers:
      - name: catalog-container
        image: catalog-service:v1 # Image name built locally in Minikube
        imagePullPolicy: Never # Crucial: tells Kubernetes to use the local image
        ports:
        - containerPort: 3000 # The port defined in server.js
        env: # Configuration linking to the database service
        - name: DB_HOST
          value: "catalog-db-service"
        - name: DB_PORT
          value: "27017"
---
# 2. Service to expose the Catalog Service externally (for Postman testing)
apiVersion: v1
kind: Service
metadata:
  name: catalog-service # Internal DNS name
spec:
  selector:
    app: catalog-service
  ports:
    - protocol: TCP
      port: 8081 # External Port (different from User Service 8080)
      targetPort: 3000 # Maps to the containerPort
  type: NodePort # Allows external access via minikube IP

  ```

#### C. Deployment Steps on Minikube

1.  **Start Minikube and Set Context**:
    ```bash
    minikube start
    eval $(minikube docker-env)
    ```
2.  **Build Images (in their respective directories)**:
    ```bash
    cd user-service/
    docker build -t user-service:v1 . 
    cd ../catalog-service/
    docker build -t catalog-service:v1 . 
    ```
3.  **Apply Manifests (from `kubernetes-manifests/` directory)**:
    ```bash
    kubectl apply -f user-db-deployment.yaml
    kubectl apply -f user-service.yaml
    # Apply catalog-db-deployment.yaml and catalog-service.yaml as well
    ```
4.  **Verify and Access Dashboard**:
    ```bash
    kubectl get pods
    minikube dashboard 
    ```
5.  **Test Service Endpoint**:
    ```bash
    minikube service user-service --url
    # Use Postman to call the resulting URL, e.g., GET <URL>/users/1
    ```
-----
Here are the complete steps to install and start Minikube on your Mac, assuming you already have Homebrew installed (the standard package manager for macOS).

## 💻 Minikube Setup on Mac

### 1\. Install Prerequisites

Before installing Minikube, you need two command-line tools: **`kubectl`** (the Kubernetes command-line tool) and **Minikube** itself.

| Tool | Purpose | Installation Command (using Homebrew) |
| :--- | :--- | :--- |
| **kubectl** | Communicates with the Kubernetes cluster (Minikube). | `brew install kubectl` |
| **Minikube** | Runs a single-node Kubernetes cluster locally. | `brew install minikube` |

### 2\. Start Minikube Cluster

You will start Minikube, specifying the driver. On Mac, the default is usually **HyperKit** (a lightweight macOS virtualization solution) or **Docker** (if you have Docker Desktop installed). Using the Docker driver is often the simplest, as it requires no extra setup.

1.  **Start Minikube using the Docker driver (Recommended)**:

    ```bash
    minikube start --driver=docker
    ```

    *If you don't have Docker Desktop running, this command will likely fail. Ensure Docker Desktop is running in your background applications.*

2.  **Start Minikube using the HyperKit driver (Alternative)**:

    ```bash
    minikube start --driver=hyperkit
    ```

    *If you choose HyperKit, you may need to install it first: `brew install hyperkit`.*

### 3\. Verify Installation

After the cluster starts, Minikube automatically configures `kubectl` to use it. You can verify the cluster status and the node.

1.  **Check Cluster Status**:
    ```bash
    minikube status
    # Output should show: host: Running, kubelet: Running, apiserver: Running, kubeconfig: Configured
    ```
2.  **Check Kubernetes Nodes**:
    ```bash
    kubectl get nodes
    # Output should show one node (e.g., 'minikube') with a status of 'Ready'.
    ```

-----

## 🛠️ Essential Steps for the Assignment

Once Minikube is running, execute these commands, which are **critical** for deploying your microservices:

### A. Point Docker to Minikube's Daemon

This command tells your local Docker client to use the Docker daemon **inside** the Minikube virtual machine. This is how you allow your locally built images (`user-service:v1`, etc.) to be seen by Kubernetes **without** having to push them to Docker Hub.

```bash
eval $(minikube docker-env)
```

### B. Build Your Images

Now, when you run `docker build` in your service directories, the images will reside inside your Minikube cluster, ready for deployment.

```bash
# Example for User Service:
cd user-service/
docker build -t user-service:v1 . 
```

### C. Deploy and Access Dashboard

1.  **Deploy your YAML files**:
    ```bash
    kubectl apply -f kubernetes-manifests/user-service.yaml
    # etc.
    ```
2.  **Access the Dashboard** (Required for assignment snapshot):
    ```bash
    minikube dashboard
    ```
-----


