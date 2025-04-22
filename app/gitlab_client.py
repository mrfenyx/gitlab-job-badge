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

def get_test_case_status(project_id, testsuite_name, testcase_name, branch=None):
    headers = get_headers()

    # Step 1: Get list of pipelines (filtered by branch if provided)
    if branch:
        url = f"{current_app.config['GITLAB_API_URL']}/projects/{project_id}/pipelines?ref={branch}&order_by=id&sort=desc"
    else:
        url = f"{current_app.config['GITLAB_API_URL']}/projects/{project_id}/pipelines?order_by=id&sort=desc"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None

    pipelines = response.json()

    # Step 2: Search pipelines for one that contains the target job (test suite name)
    for pipeline in pipelines:
        pipeline_id = pipeline["id"]

        # Get jobs for the pipeline
        jobs_url = f"{current_app.config['GITLAB_API_URL']}/projects/{project_id}/pipelines/{pipeline_id}/jobs"
        jobs_response = requests.get(jobs_url, headers=headers)
        if jobs_response.status_code != 200:
            continue

        jobs = jobs_response.json()
        if not any(job["name"] == testsuite_name for job in jobs):
            continue  # This pipeline doesn't contain the desired job

        # Step 3: Found a matching job; now get test report
        report_url = f"{current_app.config['GITLAB_API_URL']}/projects/{project_id}/pipelines/{pipeline_id}/test_report"
        report_response = requests.get(report_url, headers=headers)
        if report_response.status_code != 200:
            return None

        report = report_response.json()
        # print(report)
        for suite in report.get("test_suites", []):
            if suite["name"] == testsuite_name:
                print(f"Found test suite: {suite['name']}")
                for test_case in suite.get("test_cases", []):
                    print(f"Found test case: _{test_case['name']}_")
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

        return None  # Found job but not the test case

    return None  # No pipeline with the specified job found
