# Verification Steps for AI Resume Analysis Module

Follow these steps to verify the complete testing and verification system.

### Step 1
**Action:**
Call `GET /api/v1/llm/health`

**Expected:**
`status = healthy`

### Step 2
**Action:**
Call `GET /api/v1/ai-analysis/health`

**Expected:**
`analysis_module = ready`

### Step 3
**Action:**
Call `POST /api/v1/ai-analysis/test`

**Expected:**
- `objective_feedback` populated
- `missing_skills` contains Docker and AWS
- `improvement_recommendations` length > 0
- `interview_preparation_advice` length > 0

### Step 4
**Action:**
Stop Ollama (stop the service or kill the process) and call the test endpoint again.

**Expected:**
Meaningful error returned (e.g., Connection Error or 500 internal error).

### Step 5
**Action:**
Check logs (in your console or log files).

Prompt and response are successfully logged, including response times and any parsing errors.

---

# Verification Steps for Interview Question Generator

### Step 1: Health Check
**Action:**
Call `GET /api/v1/interview/health`

**Expected:**
`status = ready` and `llm_connected = true`

### Step 2: Generation and Validation Test
**Action:**
Call `POST /api/v1/interview/test`

**Expected:**
- Valid JSON returns with `technical_questions`, `project_questions`, `hr_questions`.
- Each category contains `easy`, `medium`, and `hard` arrays.
- Each array contains at least 3 non-empty questions.
- If any validation fails, the API returns a 500 Server Error detailing what was missing (e.g. "Validation failed: Expected at least 3 easy questions in technical_questions, got 2.")

### Step 3: Logging Check
**Action:**
Check your server console.

**Expected:**
You should see:
- `Prompt sent:`
- `Response received:` (raw Ollama output)
- `Question count generated: X` (where X is the total number of questions, e.g., 27)
- `Response generated in X.XXs`
