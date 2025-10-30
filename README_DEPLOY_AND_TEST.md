# 📚 Scalable Services — Online Bookstore (Full Deployment & Testing Guide)

This repository implements a **Microservices-based Online Bookstore** for the *Scalable Services* course assignment.  
It includes backend services, database layers, an API gateway, and a lightweight frontend for testing.

---

## 🧩 Project Overview

### Microservices Implemented
| Service | Stack | Port | Responsibility |
|----------|--------|------|----------------|
| **user-service** | Flask + PostgreSQL | 5000 | Create / Get users |
| **catalog-service** | Node.js + Express + MongoDB | 3000 | Create / List / Get books |
| **review-service** | Node.js + Express + MongoDB | 3001 | Post / Get book reviews |
| **order-service** | Flask + PostgreSQL | 5002 | Create / Get orders |
| **api-gateway** | Nginx | 80 (NodePort 30080) | Routes `/users`, `/books`, `/orders`, `/reviews` |
| **demo-frontend** | Nginx (HTML + JS) | 80 (NodePort 31000) | UI for testing all services |

### Databases
- **PostgreSQL** — used by `user-service` & `order-service`
- **MongoDB** — used by `catalog-service` & `review-service`

---

## 🗂 Directory Structure
scalable-services/
├─ user-service/
├─ catalog-service/
├─ review-service/
├─ order-service/
├─ frontend/
├─ k8s/
│  ├─ gateway/
│  ├─ frontend/
│  ├─ (postgres, mongo, and all service manifests)
├─ docker-compose.yml
└─ README.md

---
## ⚙️ Quick Local Run (Docker Compose)

Run **only `user-service` + PostgreSQL** locally (fast test):

```bash
docker compose up --build

Test:
curl http://localhost:5001/health
curl -X POST http://localhost:5001/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","email":"alice@example.com"}'
Stop:
docker compose down

☸️ Full Deployment on Minikube

🪄 Step 1 — Start Minikube + Set Docker Env
minikube start
eval $(minikube -p minikube docker-env)

🧱 Step 2 — Build Docker Images
docker build -t ss-project-user-service:latest ./user-service
docker build -t catalog-service:latest ./catalog-service
docker build -t review-service:latest ./review-service
docker build -t order-service:latest ./order-service
docker build -t demo-frontend:latest ./frontend

🗄 Step 3 — Apply Kubernetes Manifests
# Databases
kubectl apply -f k8s/postgres-secret.yaml
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml

kubectl apply -f k8s/mongo-pvc.yaml
kubectl apply -f k8s/mongo-deploy.yaml

# Core services
kubectl apply -f k8s/user-deployment.yaml
kubectl apply -f k8s/user-service.yaml
kubectl apply -f k8s/catalog-deploy.yaml
kubectl apply -f k8s/catalog-service.yaml
kubectl apply -f k8s/review-deploy.yaml
kubectl apply -f k8s/review-service.yaml
kubectl apply -f k8s/order-deploy.yaml
kubectl apply -f k8s/order-service.yaml

# Gateway + Frontend
kubectl apply -f k8s/gateway/gateway-configmap.yaml
kubectl apply -f k8s/gateway/gateway-deployment.yaml
kubectl apply -f k8s/gateway/gateway-service.yaml
kubectl apply -f k8s/frontend/frontend-deployment.yaml
kubectl apply -f k8s/frontend/frontend-service.yaml

🧾 Step 4 — Initialize Database Tables
kubectl apply -f k8s/init-users-table-job.yaml
kubectl apply -f k8s/init-orders-job.yaml
kubectl logs job/init-users-table --tail=200
kubectl delete job init-users-table
kubectl delete job init-orders

🔍 Step 5 — Watch Everything Start
kubectl get pods -w
kubectl get svc -o wide
kubectl get pvc

🌐 Accessing the App

✅ Option 1 — Port-Forward (Recommended)
kubectl port-forward svc/api-gateway 30080:80 &
kubectl port-forward svc/demo-frontend 31000:80 &

Then open:
	•	Frontend → http://localhost:31000￼
	•	Set Gateway URL → http://localhost:30080

🧪 End-to-End Test (Frontend → Gateway → Services)

Using the Demo UI
	1.	Open the frontend (http://localhost:31000)
	2.	Enter Gateway URL → http://localhost:30080
	3.	Click:
	•	Create Book → see JSON output
	•	List Books → verify book appears
	•	Create User → verify user ID
	•	Place Order → provide user ID + book ID
	4.	Verify order is created.
            # Create Book
            curl -X POST http://localhost:30080/books \
              -H "Content-Type: application/json" \
              -d '{"title":"Demo Book","author":"You","price":9.99}'
            
            # Create User
            curl -X POST http://localhost:30080/users \
              -H "Content-Type: application/json" \
              -d '{"name":"Bob","email":"bob@example.com"}'
            
            # Place Order (replace <BOOK_ID>)
            curl -X POST http://localhost:30080/orders \
              -H "Content-Type: application/json" \
              -d '{"user_id":1,"book_id":"<BOOK_ID>","qty":1}'
            
            # Check Order
            curl http://localhost:30080/orders/1
