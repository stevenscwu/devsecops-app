import json
import os
import openai
import logging
import azure.functions as func
from collections import Counter, defaultdict


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("🔹 Azure Function triggered")

    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    key = os.environ.get("AZURE_OPENAI_KEY")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")

    if not endpoint or not key or not deployment:
        logging.error("❌ Missing Azure OpenAI environment variables.")
        return func.HttpResponse("Server misconfiguration.", status_code=500)

    try:
        data = req.get_json()
    except Exception as e:
        logging.error(f"❌ Failed to parse input JSON: {e}")
        return func.HttpResponse("Invalid JSON body.", status_code=400)

    if not data:
        return func.HttpResponse("No issues found in payload.", status_code=200)

    # Combine issues from both SonarQube and ESLint
    issues = data.get("backend_issues", {}).get("issues", []) + data.get("frontend_issues", [])

    if not issues:
        return func.HttpResponse("No issues to analyze.", status_code=200)

    # Aggregate data
    rule_counter = Counter()
    file_counter = Counter()
    severity_counter = Counter()
    sample_messages = []

    for issue in issues:
        file = issue.get("component", issue.get("filePath", "unknown")).split(":")[-1]
        rule = issue.get("rule", issue.get("ruleId", "unknown"))
        severity = issue.get("severity", issue.get("severity", "UNKNOWN"))
        msg = issue.get("message", issue.get("message", ""))

        rule_counter[rule] += 1
        file_counter[file] += 1
        severity_counter[severity] += 1

        if msg:
            sample_messages.append(f"{file}: {msg}")

    # Build prompt
    prompt = f"""
You are a senior security engineer reviewing static analysis reports.

Please summarize the scan results with the following sections:
1. Top 5 most common rule violations
2. Files with the most issues
3. Severity distribution (blocker, critical, major, minor, info)
4. Three actionable recommendations to improve code security or maintainability
5. Sample findings

Rule frequency:
{json.dumps(rule_counter.most_common(5), indent=2)}

Files with most issues:
{json.dumps(file_counter.most_common(5), indent=2)}

Severity breakdown:
{json.dumps(severity_counter, indent=2)}

Sample findings:
{json.dumps(sample_messages[:5], indent=2)}
"""

    # GPT-4 call
    try:
        openai.api_type = "azure"
        openai.api_base = endpoint
        openai.api_key = key
        openai.api_version = "2024-02-15-preview"

        response = openai.ChatCompletion.create(
            engine=deployment,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful and precise security advisor. Output should be markdown."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=1000,
            temperature=0.3
        )

        summary = response["choices"][0]["message"]["content"]
        return func.HttpResponse(summary, status_code=200)

    except Exception as e:
        logging.error(f"❌ GPT-4 API call failed: {e}")
        return func.HttpResponse(f"Internal server error: {e}", status_code=500)
