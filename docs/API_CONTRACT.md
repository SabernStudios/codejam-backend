# CodeJam Backend API Contract

This document tells the frontend how to communicate with the CodeJam backend.

Current backend status:

- No login/security yet
- Local SQLite database
- JSON API
- Backend runs locally on port 8000

---

## Base URL

Local backend URL:

```text
http://127.0.0.1:8000
```

Interactive FastAPI docs:

```text
http://127.0.0.1:8000/docs
```

---

# Current Endpoints

## Health Check

### GET `/health`

Used to check whether the backend is running.

### Response

```json
{
  "status": "ok"
}
```

---

# Submissions

A submission represents one team's CodeJam project.

---

## Create Submission

### POST `/submissions`

Creates a new project submission.

### Request Body

```json
{
  "team_name": "Byte Knights",
  "team_members": "Alex, Sam, Jordan",
  "contact_email": "student@example.com",
  "project_title": "Study Timer",
  "description": "A Pomodoro timer for students.",
  "category": "Website/App",
  "project_url": "https://example.com",
  "github_url": "https://github.com/example/project",
  "demo_video_url": null
}
```

### Field Notes

| Field | Type | Required? | Notes |
|---|---|---:|---|
| `team_name` | string | Yes | Name of the team |
| `team_members` | string | Yes | Can be comma-separated names |
| `contact_email` | string | Yes | Must be a valid email |
| `project_title` | string | Yes | Title of the project |
| `description` | string | Yes | Project description |
| `category` | string | Yes | Example: Game, Website/App, Tool, Beginner |
| `project_url` | string | Yes | Must be a valid URL |
| `github_url` | string or null | No | Optional source code link |
| `demo_video_url` | string or null | No | Optional demo video link |

### Example Response

```json
{
  "id": 1,
  "team_name": "Byte Knights",
  "team_members": "Alex, Sam, Jordan",
  "contact_email": "student@example.com",
  "project_title": "Study Timer",
  "description": "A Pomodoro timer for students.",
  "category": "Website/App",
  "project_url": "https://example.com/",
  "github_url": "https://github.com/example/project",
  "demo_video_url": null
}
```

---

## Get All Submissions

### GET `/submissions`

Returns all project submissions.

### Example Response

```json
[
  {
    "id": 1,
    "team_name": "Byte Knights",
    "team_members": "Alex, Sam, Jordan",
    "contact_email": "student@example.com",
    "project_title": "Study Timer",
    "description": "A Pomodoro timer for students.",
    "category": "Website/App",
    "project_url": "https://example.com/",
    "github_url": "https://github.com/example/project",
    "demo_video_url": null
  }
]
```

---

## Get One Submission

### GET `/submissions/{submission_id}`

Returns one project submission by ID.

### Example Request

```text
GET /submissions/1
```

### Example Response

```json
{
  "id": 1,
  "team_name": "Byte Knights",
  "team_members": "Alex, Sam, Jordan",
  "contact_email": "student@example.com",
  "project_title": "Study Timer",
  "description": "A Pomodoro timer for students.",
  "category": "Website/App",
  "project_url": "https://example.com/",
  "github_url": "https://github.com/example/project",
  "demo_video_url": null
}
```

### If Not Found

```json
{
  "detail": "Submission not found"
}
```

Status code:

```text
404
```

---

## Update Submission

### PUT `/submissions/{submission_id}`

Updates an existing project submission.

This endpoint supports partial updates, meaning the frontend only needs to send the fields that changed.

### Example Request

```text
PUT /submissions/1
```

### Example Request Body

```json
{
  "project_title": "Updated Study Timer",
  "description": "An updated Pomodoro timer for students.",
  "project_url": "https://updated-example.com"
}
```

### Example Response

```json
{
  "id": 1,
  "team_name": "Byte Knights",
  "team_members": "Alex, Sam, Jordan",
  "contact_email": "student@example.com",
  "project_title": "Updated Study Timer",
  "description": "An updated Pomodoro timer for students.",
  "category": "Website/App",
  "project_url": "https://updated-example.com/",
  "github_url": "https://github.com/example/project",
  "demo_video_url": null
}
```

### Fields That Can Be Updated

```text
team_name
team_members
contact_email
project_title
description
category
project_url
github_url
demo_video_url
```

### If Not Found

```json
{
  "detail": "Submission not found"
}
```

Status code:

```text
404
```

---

# Scores

A score represents one judge's rating for one submission.

Each rubric category is scored from 1 to 10.

---

## Create Score

### POST `/scores`

Creates a judge score for a submission.

### Request Body

```json
{
  "submission_id": 1,
  "judge_name": "Test Judge",
  "creativity": 8,
  "functionality": 7,
  "technical_effort": 9,
  "presentation": 8,
  "comments": "Good project idea and solid demo."
}
```

### Field Notes

| Field | Type | Required? | Notes |
|---|---|---:|---|
| `submission_id` | integer | Yes | The ID of the submission being scored |
| `judge_name` | string | Yes | Name of the judge |
| `creativity` | integer | Yes | 1–10 |
| `functionality` | integer | Yes | 1–10 |
| `technical_effort` | integer | Yes | 1–10 |
| `presentation` | integer | Yes | 1–10 |
| `comments` | string or null | No | Optional judge comments |

### Example Response

```json
{
  "id": 1,
  "submission_id": 1,
  "judge_name": "Test Judge",
  "creativity": 8,
  "functionality": 7,
  "technical_effort": 9,
  "presentation": 8,
  "comments": "Good project idea and solid demo."
}
```

### If Submission Does Not Exist

```json
{
  "detail": "Submission not found"
}
```

Status code:

```text
404
```

### Invalid Score Example

If the frontend sends a score outside 1–10, such as:

```json
{
  "submission_id": 1,
  "judge_name": "Test Judge",
  "creativity": 100,
  "functionality": 7,
  "technical_effort": 9,
  "presentation": 8,
  "comments": "Invalid example."
}
```

FastAPI should reject it because scores must be between 1 and 10.

---

## Get All Scores

### GET `/scores`

Returns all judge scores.

### Example Response

```json
[
  {
    "id": 1,
    "submission_id": 1,
    "judge_name": "Test Judge",
    "creativity": 8,
    "functionality": 7,
    "technical_effort": 9,
    "presentation": 8,
    "comments": "Good project idea and solid demo."
  }
]
```

---

## Get Scores for One Submission

### GET `/scores/submission/{submission_id}`

Returns all judge scores for one specific submission.

### Example Request

```text
GET /scores/submission/1
```

### Example Response

```json
[
  {
    "id": 1,
    "submission_id": 1,
    "judge_name": "Test Judge",
    "creativity": 8,
    "functionality": 7,
    "technical_effort": 9,
    "presentation": 8,
    "comments": "Good project idea and solid demo."
  }
]
```

---

# Leaderboard

The leaderboard ranks submissions based on average judge scores.

---

## Get Leaderboard

### GET `/leaderboard`

Returns all scored submissions ranked from highest total score to lowest total score.

Submissions with no scores are currently not included in the leaderboard.

### Scoring Formula

For each submission:

```text
average_creativity = average of all creativity scores
average_functionality = average of all functionality scores
average_technical_effort = average of all technical effort scores
average_presentation = average of all presentation scores

total_score = average_creativity + average_functionality + average_technical_effort + average_presentation
```

Maximum possible score:

```text
40
```

### Example Response

```json
[
  {
    "submission_id": 1,
    "project_title": "Study Timer",
    "team_name": "Byte Knights",
    "category": "Website/App",
    "average_creativity": 8.0,
    "average_functionality": 7.0,
    "average_technical_effort": 9.0,
    "average_presentation": 8.0,
    "total_score": 32.0,
    "number_of_scores": 1
  }
]
```

### Response Fields

| Field | Type | Meaning |
|---|---|---|
| `submission_id` | integer | ID of the project submission |
| `project_title` | string | Project title |
| `team_name` | string | Team name |
| `category` | string | Project category |
| `average_creativity` | number | Average creativity score |
| `average_functionality` | number | Average functionality score |
| `average_technical_effort` | number | Average technical effort score |
| `average_presentation` | number | Average presentation/demo score |
| `total_score` | number | Sum of the four average category scores |
| `number_of_scores` | integer | Number of judges who scored the submission |

---

# Frontend Connection Notes

## Local Development

Backend local URL:

```text
http://127.0.0.1:8000
```

Common frontend local URLs:

```text
http://localhost:3000
http://127.0.0.1:3000
http://localhost:5173
http://127.0.0.1:5173
```

The backend should allow these origins through CORS during local development.

---

## Example Frontend Fetch: Create Submission

```javascript
async function createSubmission() {
  const response = await fetch("http://127.0.0.1:8000/submissions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      team_name: "Byte Knights",
      team_members: "Alex, Sam, Jordan",
      contact_email: "student@example.com",
      project_title: "Study Timer",
      description: "A Pomodoro timer for students.",
      category: "Website/App",
      project_url: "https://example.com",
      github_url: "https://github.com/example/project",
      demo_video_url: null
    })
  });

  const data = await response.json();
  console.log(data);
}
```

---

## Example Frontend Fetch: Get Submissions

```javascript
async function getSubmissions() {
  const response = await fetch("http://127.0.0.1:8000/submissions");
  const data = await response.json();
  console.log(data);
}
```

---

## Example Frontend Fetch: Create Score

```javascript
async function createScore() {
  const response = await fetch("http://127.0.0.1:8000/scores", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      submission_id: 1,
      judge_name: "Test Judge",
      creativity: 8,
      functionality: 7,
      technical_effort: 9,
      presentation: 8,
      comments: "Good project idea and solid demo."
    })
  });

  const data = await response.json();
  console.log(data);
}
```

---

## Example Frontend Fetch: Get Leaderboard

```javascript
async function getLeaderboard() {
  const response = await fetch("http://127.0.0.1:8000/leaderboard");
  const data = await response.json();
  console.log(data);
}
```

---

# Current MVP User Flow

The intended frontend/backend flow is:

```text
Student/team fills out project submission form
↓
Frontend sends POST /submissions
↓
Backend saves submission to SQLite
↓
Admin/judge can view submissions with GET /submissions
↓
Judge scores project with POST /scores
↓
Frontend gets rankings with GET /leaderboard
↓
Leaderboard displays ranked results
```

---

# Current MVP Limitations

These are intentionally not included yet:

- No student accounts
- No judge login
- No admin login
- No file uploads
- No email verification
- No password reset
- No team join codes
- No deployment configuration yet
- No production database yet

Security will be added later after core functionality works.

---

# Current Backend Routes Summary

```text
GET  /
GET  /health

POST /submissions
GET  /submissions
GET  /submissions/{submission_id}
PUT  /submissions/{submission_id}

POST /scores
GET  /scores
GET  /scores/submission/{submission_id}

GET  /leaderboard
```