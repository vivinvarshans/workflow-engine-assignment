# Deployment Guide

This guide covers deploying the Workflow Engine to various environments.

## Table of Contents

- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Cloud Platforms](#cloud-platforms)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

---

## Local Development

### Prerequisites

- Python 3.9+
- pip
- Virtual environment

### Setup

```bash
# Clone repository
git clone <repository-url>
cd workflow-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify setup
python verify_setup.py

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Development Server

```bash
# With auto-reload
uvicorn app.main:app --reload

# With custom port
uvicorn app.main:app --reload --port 8001

# With debug logging
uvicorn app.main:app --reload --log-level debug
```

---

## Docker Deployment

### Build Image

```bash
# Build
docker build -t workflow-engine:latest .

# Run
docker run -p 8000:8000 workflow-engine:latest
```

### Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and start
docker-compose up -d --build
```

### Docker Configuration

**Environment Variables:**
```yaml
environment:
  - DATABASE_URL=sqlite:///./data/workflow_engine.db
  - LOG_LEVEL=INFO
  - MAX_WORKERS=4
```

**Volume Mounts:**
```yaml
volumes:
  - ./data:/app/data  # Database persistence
  - ./logs:/app/logs  # Log files
```

---

## Production Deployment

### Using Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Systemd Service

Create `/etc/systemd/system/workflow-engine.service`:

```ini
[Unit]
Description=Workflow Engine API
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/workflow-engine
Environment="PATH=/opt/workflow-engine/venv/bin"
ExecStart=/opt/workflow-engine/venv/bin/gunicorn \
  app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable workflow-engine
sudo systemctl start workflow-engine
sudo systemctl status workflow-engine
```

### Nginx Reverse Proxy

Create `/etc/nginx/sites-available/workflow-engine`:

```nginx
upstream workflow_engine {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://workflow_engine;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws/ {
        proxy_pass http://workflow_engine;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/workflow-engine /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL/TLS with Let's Encrypt

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d api.example.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## Cloud Platforms

### AWS Elastic Beanstalk

**Dockerfile:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ ./app/
EXPOSE 8000
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

**Deploy:**
```bash
eb init -p docker workflow-engine
eb create workflow-engine-env
eb deploy
```

### Google Cloud Run

**Build and deploy:**
```bash
# Build image
gcloud builds submit --tag gcr.io/PROJECT_ID/workflow-engine

# Deploy
gcloud run deploy workflow-engine \
  --image gcr.io/PROJECT_ID/workflow-engine \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Heroku

**Procfile:**
```
web: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

**Deploy:**
```bash
heroku create workflow-engine
git push heroku main
heroku open
```

### Azure Container Instances

```bash
# Create resource group
az group create --name workflow-engine-rg --location eastus

# Create container
az container create \
  --resource-group workflow-engine-rg \
  --name workflow-engine \
  --image workflow-engine:latest \
  --dns-name-label workflow-engine \
  --ports 8000
```

### Kubernetes

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: workflow-engine
spec:
  replicas: 3
  selector:
    matchLabels:
      app: workflow-engine
  template:
    metadata:
      labels:
        app: workflow-engine
    spec:
      containers:
      - name: workflow-engine
        image: workflow-engine:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          value: "postgresql://user:pass@db:5432/workflows"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: workflow-engine
spec:
  selector:
    app: workflow-engine
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

**Deploy:**
```bash
kubectl apply -f deployment.yaml
kubectl get services
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | Database connection string | sqlite:///./workflow_engine.db |
| LOG_LEVEL | Logging level | INFO |
| MAX_WORKERS | Number of worker processes | 4 |
| HOST | Server host | 0.0.0.0 |
| PORT | Server port | 8000 |

### Database Configuration

**SQLite (Development):**
```python
DATABASE_URL = "sqlite:///./workflow_engine.db"
```

**PostgreSQL (Production):**
```python
DATABASE_URL = "postgresql://user:password@localhost:5432/workflows"
```

**MySQL:**
```python
DATABASE_URL = "mysql+pymysql://user:password@localhost:3306/workflows"
```

### Logging Configuration

**Python logging:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('workflow_engine.log'),
        logging.StreamHandler()
    ]
)
```

---

## Monitoring

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/
```

### Metrics

**Prometheus metrics (to be implemented):**
```python
from prometheus_client import Counter, Histogram

workflow_executions = Counter('workflow_executions_total', 'Total workflow executions')
workflow_duration = Histogram('workflow_duration_seconds', 'Workflow execution duration')
```

### Logging

**Application logs:**
```bash
# View logs
tail -f workflow_engine.log

# Search logs
grep "ERROR" workflow_engine.log

# Follow logs in Docker
docker-compose logs -f workflow-engine
```

### Monitoring Tools

**Recommended tools:**
- **Prometheus** - Metrics collection
- **Grafana** - Visualization
- **ELK Stack** - Log aggregation
- **Sentry** - Error tracking
- **New Relic** - APM

---

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Use different port
uvicorn app.main:app --port 8001
```

**Database locked:**
```bash
# Remove database file
rm workflow_engine.db

# Restart application
```

**Import errors:**
```bash
# Verify Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Memory issues:**
```bash
# Check memory usage
docker stats

# Increase memory limit
docker run -m 1g workflow-engine
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
uvicorn app.main:app --log-level debug

# Python debugger
python -m pdb app/main.py
```

### Performance Issues

**Database optimization:**
```sql
-- Add indexes
CREATE INDEX idx_runs_graph_id ON runs(graph_id);
CREATE INDEX idx_runs_status ON runs(status);

-- Analyze tables
ANALYZE runs;
ANALYZE graphs;
```

**Connection pooling:**
```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

---

## Security Checklist

- [ ] Use HTTPS in production
- [ ] Enable authentication
- [ ] Set up rate limiting
- [ ] Configure CORS properly
- [ ] Use environment variables for secrets
- [ ] Keep dependencies updated
- [ ] Enable security headers
- [ ] Set up firewall rules
- [ ] Regular security audits
- [ ] Backup database regularly

---

## Backup and Recovery

### Database Backup

**SQLite:**
```bash
# Backup
cp workflow_engine.db workflow_engine.db.backup

# Restore
cp workflow_engine.db.backup workflow_engine.db
```

**PostgreSQL:**
```bash
# Backup
pg_dump workflows > backup.sql

# Restore
psql workflows < backup.sql
```

### Automated Backups

**Cron job:**
```bash
# Add to crontab
0 2 * * * /path/to/backup.sh

# backup.sh
#!/bin/bash
DATE=$(date +%Y%m%d)
cp workflow_engine.db backups/workflow_engine_$DATE.db
find backups/ -mtime +30 -delete
```

---

## Scaling

### Vertical Scaling

- Increase CPU cores
- Add more RAM
- Use faster storage (SSD)
- Optimize database queries

### Horizontal Scaling

**Load balancer configuration:**
```nginx
upstream workflow_engines {
    least_conn;
    server 10.0.1.10:8000;
    server 10.0.1.11:8000;
    server 10.0.1.12:8000;
}
```

**Shared database:**
- Use PostgreSQL or MySQL
- Enable connection pooling
- Set up read replicas

**Caching:**
- Redis for session storage
- Memcached for query results
- CDN for static assets

---

## Maintenance

### Updates

```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Database migrations
alembic upgrade head

# Restart service
sudo systemctl restart workflow-engine
```

### Monitoring

```bash
# Check service status
sudo systemctl status workflow-engine

# View recent logs
sudo journalctl -u workflow-engine -n 100

# Check disk space
df -h

# Check memory
free -h
```

---

## Support

For deployment issues:
1. Check logs first
2. Review this guide
3. Search existing issues
4. Create new issue with details

---

## Additional Resources

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Uvicorn Deployment](https://www.uvicorn.org/deployment/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)
