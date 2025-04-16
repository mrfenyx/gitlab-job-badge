from flask import Blueprint, request, redirect, render_template, Response
from .gitlab_client import get_job_status

bp = Blueprint("routes", __name__)

def status_color(status):
    return {
        "success": "#4c1",
        "failed": "#e05d44",
        "running": "#dfb317",
        "pending": "#dfb317",
        "canceled": "#9f9f9f",
        "manual": "#007ec6"
    }.get(status, "#9f9f9f")

def estimate_text_width(text):
    avg_char_width = 6  # tweak based on font and size
    padding = 10
    return len(text) * avg_char_width + padding

@bp.route("/badge")
def badge():
    project_id = request.args.get("projectid")
    branch = request.args.get("branch")
    job_name = request.args.get("job")

    if not project_id or not branch or not job_name:
        return "Missing parameters", 400

    job_info = get_job_status(project_id, branch, job_name)
    if not job_info:
        return "Job not found", 404

    status = job_info["status"]
    job_url = job_info["web_url"]
    color = status_color(status)

    label_width = estimate_text_width(job_name)
    status_width = estimate_text_width(status)
    total_width = label_width + status_width

    svg = render_template(
        "badge.svg.j2",
        label=job_name,
        status=status,
        color=color,
        label_width=label_width,
        status_width=status_width,
        total_width=total_width,
        job_url=job_url  # 👈 this is new
    )

    return Response(svg, content_type="image/svg+xml")

@bp.route("/badge/link")
def badge_link():
    project_id = request.args.get("projectid")
    branch = request.args.get("branch")
    job_name = request.args.get("job")

    job_info = get_job_status(project_id, branch, job_name)
    if job_info:
        return redirect(job_info["web_url"])
    return "Job not found", 404
