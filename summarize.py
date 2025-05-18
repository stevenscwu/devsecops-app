import os
import openai

# Azure OpenAI configuration
openai.api_type = "azure"
openai.api_base = os.environ["AZURE_OPENAI_ENDPOINT"]
openai.api_key = os.environ["AZURE_OPENAI_KEY"]
openai.api_version = "2024-02-15-preview"
deployment_name = os.environ["AZURE_OPENAI_DEPLOYMENT"]

# Read SonarQube report artifact (you can change this path as needed)
report_path = "report/sonar-report.txt"
if not os.path.exists(report_path):
    raise FileNotFoundError(f"Report not found at {report_path}")

with open(report_path, "r", encoding="utf-8") as file:
    report_content = file.read()

# Call Azure OpenAI to summarize the report
response = openai.ChatCompletion.create(
    engine=deployment_name,
    messages=[
        {"role": "system", "content": "You are an expert code reviewer. Summarize and prioritize the issues from this SonarQube report."},
        {"role": "user", "content": f"Summarize the following SonarQube report:\n\n{report_content}"}
    ],
    max_tokens=1000
)

print("===== GPT-4 Summary of SonarQube Report =====")
print(response["choices"][0]["message"]["content"])
