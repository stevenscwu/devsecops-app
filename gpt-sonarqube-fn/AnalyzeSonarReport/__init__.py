import json
import os
import openai
import logging
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("🔹 Azure Function triggered")

    # Step 1: Validate environment variables
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    key = os.environ.get("AZURE_OPENAI_KEY")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")

    if not endpoint or not key or not deployment:
        logging.error(f"❌ Missing environment variables: "
                      f"Endpoint={'set' if endpoint else 'MISSING'}, "
                      f"Key={'set' if key else 'MISSING'}, "
                      f"Deployment={'set' if deployment else 'MISSING'}")
        return func.HttpResponse(
            "Server misconfiguration: missing Azure OpenAI environment variables.",
            status_code=500
        )

    # Step 2: Parse request JSON
    try:
        sonar_json = req.get_json()
        logging.info(f"✅ Received JSON with keys: {list(sonar_json.keys())}")
    except Exception as e:
        logging.error(f"❌ Failed to parse JSON: {e}")
        return func.HttpResponse("Invalid JSON body.", status_code=400)

    issues = sonar_json.get("issues", [])
    if not issues:
        logging.warning("⚠️ No issues found in input JSON.")
        return func.HttpResponse("No issues found in payload.", status_code=400)

    logging.info(f"🧩 Extracted {len(issues)} issues")

    # Step 3: Format the GPT prompt
    summary_text = ""
    for i, issue in enumerate(issues, 1):
        msg = issue.get("message", "")
        file = issue.get("component", "").split(":")[-1]
        line = issue.get("line", "?")
        severity = issue.get("severity", "")
        rule = issue.get("rule", "")
        summary_text += f"{i}. [{severity}] Line {line} in {file}: {msg} (Rule: {rule})\n"

    logging.info("📝 Prompt prepared. Preview:\n" + summary_text[:300] + "...")

    # Step 4: Call Azure OpenAI GPT-4
    try:
        openai.api_type = "azure"
        openai.api_base = endpoint
        openai.api_key = key
        openai.api_version = "2024-02-15-preview"

        response = openai.ChatCompletion.create(
            engine=deployment,
            messages=[
                {"role": "system", "content": "You are a secure code reviewer."},
                {"role": "user", "content": f"Summarize and prioritize these SonarQube issues:\n{summary_text}"}
            ],
            max_tokens=1000,
            temperature=0.3
        )

        result = response["choices"][0]["message"]["content"]
        logging.info("✅ GPT-4 responded successfully")
        return func.HttpResponse(result, status_code=200)

    except Exception as e:
        logging.error(f"❌ GPT-4 API call failed: {e}")
        return func.HttpResponse(f"Internal server error: {e}", status_code=500)
