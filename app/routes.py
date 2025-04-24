from flask import Blueprint, request, redirect, render_template, Response, session, current_app, abort, url_for
from .gitlab_client import get_job_status, get_test_case_status, get_test_cases_for_suite
from urllib.parse import urlencode
import hmac
import hashlib

bp = Blueprint("routes", __name__)

# --- Security Helpers ---

def estimate_text_width(text):
    avg_char_width = 7
    padding = 10
    return len(text) * avg_char_width + padding

def status_color(status):
    return {
        "success": "#4c1",
        "failed": "#e05d44",
        "running": "#dfb317",
        "pending": "#dfb317",
        "canceled": "#9f9f9f",
        "manual": "#007ec6"
    }.get(status, "#9f9f9f")

def generate_signature(params: dict, secret: str) -> str:
    base_string = urlencode(sorted((k, v) for k, v in params.items() if k != "sig"))
    return hmac.new(secret.encode(), base_string.encode(), hashlib.sha256).hexdigest()

def verify_signature():
    if not current_app.config.get("AZURE_SSO"):
        return True
    provided_sig = request.args.get("sig")
    if not provided_sig:
        return False
    params = dict(request.args)
    calculated_sig = generate_signature(params, current_app.config["FLASK_SECRET_KEY"])
    return hmac.compare_digest(provided_sig, calculated_sig)

# --- Badge Routes ---

@bp.route("/badge")
def badge():
    if not verify_signature():
        return "Unauthorized", 401

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
        job_url=job_url
    )

    return Response(svg, content_type="image/svg+xml")

@bp.route("/badge/link")
def badge_link():
    if not verify_signature():
        return "Unauthorized", 401

    project_id = request.args.get("projectid")
    branch = request.args.get("branch")
    job_name = request.args.get("job")

    job_info = get_job_status(project_id, branch, job_name)
    if job_info:
        return redirect(job_info["web_url"])
    return "Job not found", 404

@bp.route("/test")
def test_case_badge():
    if not verify_signature():
        return "Unauthorized", 401

    project_id = request.args.get("projectid")
    testsuite = request.args.get("testsuite")
    classname = request.args.get("classname")
    branch = request.args.get("branch")
    simple = request.args.get("simple", "false").lower() == "true"

    if not project_id or not testsuite or not classname:
        return "Missing parameters", 400

    test_info = get_test_case_status(project_id, testsuite, classname, branch)
    if not test_info:
        return "Test not found", 404

    status = test_info["status"]
    color = status_color(status)

    if simple:
        label = ""
        label_width = 0
        status_width = estimate_text_width(status)
        total_width = status_width
    else:
        label = classname[:37] + "..."
        label_width = estimate_text_width(label) - 40
        status_width = estimate_text_width(status)
        total_width = label_width + status_width

    svg = render_template(
        "badge.svg.j2",
        label=label,
        status=status,
        color=color,
        label_width=label_width,
        status_width=status_width,
        total_width=total_width,
        job_url=test_info.get("web_url")
    )

    return Response(svg, content_type="image/svg+xml")

@bp.route("/helper")
def badge_helper():
    if current_app.config.get("AZURE_SSO") and "user" not in session:
        return redirect(url_for("routes.login"))

    project_id = request.args.get("projectid")
    testsuite = request.args.get("testsuite")
    branch = request.args.get("branch", "").strip()
    simple = request.args.get("simple") == "on"

    if not project_id or not testsuite:
        return "Missing 'projectid' or 'testsuite' in query parameters", 400

    test_cases = get_test_cases_for_suite(project_id, testsuite, branch or None)
    base_url = request.host_url.rstrip("/")
    badge_urls = []

    for case in test_cases:
        name = case["name"]
        params = {
            "projectid": project_id,
            "testsuite": testsuite,
            "classname": name
        }
        if branch:
            params["branch"] = branch
        if simple:
            params["simple"] = "true"

        if current_app.config.get("AZURE_SSO"):
            sig = generate_signature(params, current_app.config["FLASK_SECRET_KEY"])
            params["sig"] = sig

        query = urlencode(params)
        badge_urls.append((name, f"{base_url}/test?{query}"))

    return render_template(
        "helper.html.j2",
        badge_urls=badge_urls,
        projectid=project_id,
        testsuite=testsuite,
        branch=branch,
        simple=simple
    )

# --- Azure AD SSO Routes ---

@bp.route("/login")
def login():
    if not current_app.config.get("AZURE_SSO"):
        return abort(403, description="SSO is not enabled")
    redirect_uri = url_for("routes.auth_redirect", _external=True)
    return current_app.oauth.azure.authorize_redirect(redirect_uri)

@bp.route("/auth/redirect")
def auth_redirect():
    if not current_app.config.get("AZURE_SSO"):
        return abort(403, description="SSO is not enabled")
    token = current_app.oauth.azure.authorize_access_token()
    user = current_app.oauth.azure.parse_id_token(token)
    session["user"] = {
        "name": user.get("name"),
        "email": user.get("email")
    }
    return redirect(url_for("routes.badge_helper"))

@bp.route("/logout")
def logout():
    session.clear()
    return redirect("https://login.microsoftonline.com/common/oauth2/v2.0/logout")
