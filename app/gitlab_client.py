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