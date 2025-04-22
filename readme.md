# GitLab Job Badge API

This project is a lightweight Flask-based API that serves dynamic SVG badges showing the status of a GitLab CI/CD job or individual test case for a specific project.

## 🚀 Features

- Returns GitLab-style SVG badges with rounded corners
- Shows status of:
  - Latest **non-skipped job**
  - Specific **test case inside a test suite**
- Badges are **clickable**, linking to GitLab job or test report
- Dockerized and published via GitHub Actions
- Configurable via `.env`

---

## 🔧 Usage

### Job Badge Endpoint

```
GET /badge?projectid=<project_id>&branch=<branch_name>&job=<job_name>
```

Returns a badge for the latest non-skipped job execution on a branch.

### Test Badge Endpoint

```
GET /test?projectid=<project_id>&testsuite=<job_name>&classname=<test_case_name>&branch=<optional_branch>
```

Returns a badge showing the result of a specific test case in a GitLab test report. If the branch is not provided, the latest relevant pipeline is searched.

### Examples

Job:
```
GET /badge?projectid=12345&branch=main&job=test
```

Test:
```
GET /test?projectid=12345&testsuite=security&classname=security.ddos.protection
```

### Embedding in Markdown or Confluence

```
![tests](https://yourdomain.com/badge?projectid=12345&branch=main&job=test)
```

Or use an `<img>` inside a link:

```html
<a href="https://yourdomain.com/badge/link?projectid=12345&branch=main&job=test">
  <img src="https://yourdomain.com/badge?projectid=12345&branch=main&job=test" alt="Build status">
</a>
```

---

## 🛠 Configuration

Create a `.env` file with:

```
GITLAB_API_URL=https://gitlab.com/api/v4
GITLAB_WEB_URL=https://gitlab.com
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

## 📄 License

MIT License