# GitLab Job Badge API

This project is a lightweight Flask-based API that serves dynamic SVG badges showing the status of a GitLab CI/CD job or individual test case for a specific project.

## 🚀 Features

- Returns GitLab-style SVG badges with rounded corners
- Shows status of:
  - Latest **non-skipped job**
  - Specific **test case inside a test suite**
- Badges are **clickable**, linking to GitLab job or test report
- Includes a helper UI to browse test cases and generate badge links
- Copy-to-clipboard buttons for quick use
- Dockerized and easily runnable
- Configurable via `.env`

---

## 🔧 Usage

### Job Badge Endpoint

```http
GET /badge?projectid=<project_id>&branch=<branch_name>&job=<job_name>
```

Returns a badge for the latest non-skipped job execution on a branch.

### Test Badge Endpoint

```http
GET /test?projectid=<project_id>&testsuite=<job_name>&classname=<test_case_name>&branch=<optional_branch>
```

Returns a badge showing the result of a specific test case in a GitLab test report. If the branch is not provided, the latest relevant pipeline is searched.

---

### Badge URL Helper UI

Use the `/helper` page to browse test cases and generate badge links interactively:

```http
GET /helper?projectid=<project_id>&testsuite=<job_name>
```

Optional query parameters:

- `branch`: limit to a specific branch
- `simple=true`: omit `/badge/link` logic

On the page you’ll find:

- A table listing test cases
- A preview of each badge (in an iframe)
- The URL used
- A **Copy** button for quick sharing

---

### Examples

Job badge:

```http
/badge?projectid=12345&branch=main&job=test
```

Test badge:

```http
/test?projectid=12345&testsuite=MyTestSuite&classname=MyTestName
```

Helper UI:

```http
/helper?projectid=12345&testsuite=MyTestSuite
```

---

### Embedding in Markdown

```markdown
![tests](https://yourdomain.com/badge?projectid=12345&branch=main&job=test)
```

Or as a clickable badge:

```html
<a href="https://yourdomain.com/badge/link?projectid=12345&branch=main&job=test">
  <img src="https://yourdomain.com/badge?projectid=12345&branch=main&job=test" alt="Build status">
</a>
```

---

## 🛠 Configuration

Create a `.env` file with the following:

```plaintext
GITLAB_API_URL=https://gitlab.com/api/v4
GITLAB_WEB_URL=https://gitlab.com
GITLAB_ACCESS_TOKEN=your_personal_access_token
```

---

## 🐳 Docker

### Build locally

```bash
docker build -t gitlab-badge-api .
```

### Run

```bash
docker run -p 5000:5000 --env-file .env gitlab-badge-api
```

---

## 📄 License

MIT License
