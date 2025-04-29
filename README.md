[![Backend CI](https://github.com/software-students-spring2025/5-final-tralalero-tralala/actions/workflows/backend.yml/badge.svg)]
[![Frontend CI](https://github.com/software-students-spring2025/5-final-tralalero-tralala/actions/workflows/frontend.yml/badge.svg)]

# 🧭 Lost & Found @ NYU

A web platform for NYU students to report lost items and find items found by others — powered by Flask, MongoDB, and full CI/CD with Docker and GitHub Actions.

---

## 🐳 Docker Images

- [`t1mmmmm/backend`](https://hub.docker.com/r/t1mmmmm/backend)
- [`t1mmmmm/frontend`](https://hub.docker.com/r/t1mmmmm/frontend)

> 🟢 Live site: [http://167.99.148.70:3000](http://167.99.148.70:3000)
---
## Sites
🔗 Deployed frontend: [http://167.99.148.70:3000](http://167.99.148.70:3000)  
🔧 Deployed backend: [http://167.99.148.70:5001](http://167.99.148.70:5001)  

> You can still run the project locally using the instructions below.

## ⚙️ Setup Instructions (Local Dev)

### 📦 Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt
```
---

### Create Environment File

```bash
cp .env.example .env
```

edit the env file if needed, it should contain:
```bash
MONGO_URI=mongodb://mongo:27017/lostfound
SECRET_KEY=your-secret-key
DEBUG=True
```
---

## Run Full System with Docker
```bash
docker-compose up --build
```
Frontend: http://localhost:3000
Backend: http://localhost:5001
MongoDB runs internally
---

## When Done
```bash
docker-compose down
```
After Ctrl+C to stop the process and remove docker containers.

### Note
Make sure Docker Desktop is installed and running.

If ports 3000 or 5001 are busy, stop other apps or change ports in docker-compose.yml.

Each subsystem has independent CI/CD with GitHub Actions and DockerHub image push.
---

## 👨‍💻 Contributors

- [Tim Yan](https://github.com/t1mmmmm)
- [Kenny Pan](https://github.com/kenny-pan)
- [Winter Li](https://github.com/YYukin0)
- [Warren Wu](https://github.com/W0rren12)