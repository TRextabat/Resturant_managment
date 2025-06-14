# Resturant_managment
# Restaurant App - Docker Setup

This project contains the frontend (React/Next.js), backend API, Postgres database, and Redis services, all orchestrated with Docker Compose.

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed
- [Docker Compose](https://docs.docker.com/compose/install/) installed

---

## How to build and run the project

### 1. Clone the repository

```bash
git clone https://github.com/TRextabat/Resturant_managment
cd Resturant_managment
```
### 2. Build and start all container 

```bash
  docker-compose build
  docker-compose up -d
```
### 3. Access the Services
Frontend (Next.js React app): http://localhost:3000

Backend API (FastAPI or your backend): http://localhost:8500/api/v1

Postgres DB: Port 5438 (check your DB client)

Redis: Port 6379

also you coudl access swagger http://localhost:8500/api/v1/docs

### 4. Stop containers 
```bash
  docker-compose down
```

