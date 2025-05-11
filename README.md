# lead_commander
# lead_commander
# retool_dashboard

# 🧠 Lead Commander Backend

An AI-powered backend platform that provides actionable business insights, lead evaluation, and financial forecasting using GPT-4 and Supabase logging. This project exposes RESTful API endpoints via FastAPI and logs all agent activity for transparency and analytics.

---

## 🚀 Features

- ✅ GPT-4 integration for business insight generation
- ✅ Lead scoring and enrichment from structured payloads
- ✅ Lifetime value estimation based on customer metrics
- ✅ Robust error handling and fallback responses
- ✅ Automatic logging of all agent interactions to Supabase
- ✅ Designed for integration with Retool, Supabase, and frontend dashboards

---

## 🧠 Agent Capabilities

| Agent                 | Endpoint                  | Description |
|-----------------------|---------------------------|-------------|
| **Insight Agent**     | `POST /insights/generate` | Generates a summarized insight from unstructured business input |
| **Lead Intelligence** | `POST /leads/analyze`     | Analyzes a lead profile (name, title, company, intent) and returns an AI-generated assessment |
| **LTV Agent**         | `POST /leads/ltv`         | Estimates customer lifetime value using deal amounts, purchase frequency, and contract length |

Each agent includes:

- Echoed payload for debugging
- OpenAI GPT-4 processing
- Fallback response if GPT fails
- Logs sent to Supabase for auditing

---

## 📦 Supabase Logging

All agents write structured logs to a `agent_logs` table:

```sql
create table agent_logs (
  id uuid primary key default gen_random_uuid(),
  agent_type text not null,
  input_payload jsonb not null,
  output jsonb not null,
  created_at timestamp with time zone default timezone('utc', now())
);
Logged data includes:

agent_type: "insight", "lead_score", or "ltv"
input_payload: raw request body
output: final response (including GPT or fallback)
created_at: auto-generated timestamp
⚙️ Setup Instructions

Clone the Repo
git clone https://github.com/<your-username>/retool_dashboard.git
cd retool_dashboard
Configure Environment Variables
Copy .env.example and set your credentials:

cp .env.example .env
Fill in:

OPENAI_API_KEY
SUPABASE_URL
SUPABASE_SERVICE_KEY
Install Dependencies
pip install -r requirements.txt
Run the Server
uvicorn app.main:app --host 0.0.0.0 --port 10000
View API Docs
Visit:

http://localhost:10000/docs
🛡️ Error Handling

Each agent uses try/except blocks and prints error messages to the console. If OpenAI fails or input is malformed, a fallback message is returned with a non-breaking response.

📈 Future Enhancements

Supabase analytics dashboard (e.g. query by agent type, usage trends)
Async GPT processing with httpx
Agent versioning or prompt tuning per user
Slack/email delivery of insights
Admin panel via Retool
🧪 Testing Endpoints in Swagger

Visit /docs and try each:

/insights/generate
{ "input": "Revenue dropped 20% last month, but email conversions improved." }
/leads/analyze
{
  "name": "Chris Green",
  "title": "Head of Sales",
  "company": "BrightMetrics",
  "intent": "Requested case studies"
}
/leads/ltv
{
  "deal_amount": 4500,
  "repeat_purchases": 3,
  "contract_length_months": 12
}
👨‍💻 Built With

FastAPI
OpenAI GPT-4
Supabase
Render
Retool (frontend integration-ready)