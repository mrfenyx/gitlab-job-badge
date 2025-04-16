# GitLab Job Badge API

This project is a lightweight Flask-based API that serves dynamic SVG badges showing the status of a GitLab CI/CD job for a specific project, branch, and job name.

## 🚀 Features

- Returns GitLab-style SVG badges with rounded corners.
- Automatically finds the latest **non-skipped** job run.
- Badge links to the GitLab job execution.
- Supports Docker and Docker Hub publishing.
- GitHub Actions workflow with manual version tagging.

---

## 🔧 Usage

### API Endpoint

```
GET /badge?projectid=<project_id>&branch=<branch_name>&job=<job_name>
```

Returns an SVG badge showing the status of the latest non-skipped job.

### Example

```
GET /badge?projectid=12345&branch=main&job=tests
```

### Embedding in Markdown

```
[![tests](https://yourdomain.com/badge?projectid=12345&branch=main&job=tests)](https://yourdomain.com/badge/link?projectid=12345&branch=main&job=tests)
```

---

## 🛠 Configuration

Create a `.env` file with:

```
GITLAB_API_URL=https://gitlab.com/api/v4
GITLAB_ACCESS_TOKEN=your_personal_access_token
```

---

## 🐳 Docker

### Build locally

```bash
docker build -t yourusername/gitlab-badge-api:latest .
```

### Run

```bash
docker run -p 5000:5000 --env-file .env yourusername/gitlab-badge-api
```

---

## 🤖 GitHub Actions (Docker Publish)

Trigger the GitHub Action manually via the Actions tab, supplying a version like `v1.0.0`. This will:

- Build the Docker image
- Tag it with `:latest` and `:v1.0.0`
- Push both to Docker Hub

---

## 📁 Project Structure

```
gitlab-badge-api/
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── gitlab_client.py
│   └── templates/
│       └── badge.svg.j2
├── config.py
├── requirements.txt
├── Dockerfile
├── run.py
├── .env
├── .gitignore
└── .github/
    └── workflows/
        └── docker-publish.yml
```

---

## 📄 License

MIT License