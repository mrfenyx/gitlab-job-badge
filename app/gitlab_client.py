import requests
from flask import current_app

def get_headers():
    return {
        "PRIVATE-TOKEN": current_app.config["GITLAB_ACCESS_TOKEN"]
    }

def get_latest_pipeline(project_id, branch):
    url = f"{current_app.config['GITLAB_API_URL']}/projects/{project_id}/pipelines"
    params = {"ref": branch, "order_by": "id", "sort": "desc"}
    response = requests.get(url, headers=get_headers(), params=params)
    pipelines = response.json()
    return pipelines[0] if pipelines else None

def get_job_status(project_id, branch, job_name):
    url = f"{current_app.config['GITLAB_API_URL']}/projects/{project_id}/pipelines"
    params = {"ref": branch, "order_by": "id", "sort": "desc"}
    response = requests.get(url, headers=get_headers(), params=params)
    if response.status_code != 200:
        return None

    pipelines = response.json()
    for pipeline in pipelines:
        pipeline_id = pipeline["id"]
        jobs_url = f"{current_app.config['GITLAB_API_URL']}/projects/{project_id}/pipelines/{pipeline_id}/jobs"
        jobs_response = requests.get(jobs_url, headers=get_headers())
        if jobs_response.status_code != 200:
            continue

        jobs = jobs_response.json()
        for job in jobs:
            if job["name"] == job_name and job["status"] != "skipped":
                return {
                    "status": job["status"],
                    "web_url": job["web_url"]
                }
    return None

def get_test_cases_and_pipeline_id(project_id, testsuite_name, branch=None):
    headers = get_headers()

    if branch:
        url = f"{current_app.config['GITLAB_API_URL']}/projects/{project_id}/pipelines?ref={branch}&order_by=id&sort=desc"
    else:
        url = f"{current_app.config['GITLAB_API_URL']}/projects/{project_id}/pipelines?order_by=id&sort=desc"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None, None

    pipelines = response.json()
    for pipeline in pipelines:
        pipeline_id = pipeline["id"]

        jobs_url = f"{current_app.config['GITLAB_API_URL']}/projects/{project_id}/pipelines/{pipeline_id}/jobs"
        jobs_response = requests.get(jobs_url, headers=headers)
        if jobs_response.status_code != 200:
            continue

        jobs = jobs_response.json()
        if not any(job["name"] == testsuite_name for job in jobs):
            continue

        report_url = f"{current_app.config['GITLAB_API_URL']}/projects/{project_id}/pipelines/{pipeline_id}/test_report"
        report_response = requests.get(report_url, headers=headers)
        if report_response.status_code != 200:
            return None, None

        report = report_response.json()
        for suite in report.get("test_suites", []):
            if suite["name"] == testsuite_name:
                return suite.get("test_cases", []), pipeline_id

    return None, None

def get_test_case_status(project_id, testsuite_name, testcase_name, branch=None):
    headers = get_headers()
    test_cases, pipeline_id = get_test_cases_and_pipeline_id(project_id, testsuite_name, branch)

    if not test_cases or not pipeline_id:
        return None

    for test_case in test_cases:
        if test_case["name"].strip() == testcase_name.strip():
            project_url = current_app.config.get("GITLAB_WEB_URL", "https://git.flix.tech")
            project_api_url = f"{current_app.config['GITLAB_API_URL']}/projects/{project_id}"
            project_response = requests.get(project_api_url, headers=headers)

            if project_response.status_code != 200:
                return None

            project_path = project_response.json().get("path_with_namespace")

            return {
                "status": test_case["status"],
                "classname": test_case["classname"],
                "pipeline_id": pipeline_id,
                "job_name": testsuite_name,
                "web_url": f"{project_url}/{project_path}/-/pipelines/{pipeline_id}/test_report?job_name={testsuite_name}"
            }
    return None

def get_test_cases_for_suite(project_id, testsuite_name, branch=None):
    test_cases, _ = get_test_cases_and_pipeline_id(project_id, testsuite_name, branch)
    return test_cases or []
