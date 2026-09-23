# Inndhu – Frontend Error Handling Module

This is a complete runnable mini-module for **Frontend Error Handling** in a job recommendation portal.

## What this module implements

- Handles successful backend API responses.
- Handles HTTP 400, 401, 403, 404, 429 and 500 errors.
- Handles backend connection/network errors.
- Converts technical API failures into user-friendly messages.
- Shows a loading state while an API request is running.
- Provides a dismissible error alert.
- Demonstrates API error handling using dedicated test buttons.
- Includes a simple job recommendation result view.
- Includes CORS support in the demo backend.

## Requirements

- Node.js 18+ recommended
- npm

## Run

### Terminal 1 – backend

```bash
cd backend
npm start
```

Backend will run on:
http://localhost:5000

### Terminal 2 – frontend

From the project root:

```bash
npm install
npm start
```

Open the Vite URL shown in the terminal, normally:
http://localhost:5173

## Demo

1. Click **Load Job Recommendations** to test a successful API call.
2. Click **Test HTTP 400/401/403/404/429/500**.
3. The frontend catches the API error and displays a safe, friendly message instead of exposing raw backend details.
4. Stop the backend and click **Load Job Recommendations** to test the connection-error message.

## Important design point

The frontend does not directly display `serverMessage`. It maps HTTP status codes to safe user-facing text. This helps avoid exposing sensitive backend information and gives users actionable feedback.

## Suggested presentation explanation

"My module is responsible for frontend error handling. It catches failed API requests, identifies HTTP status codes, maps them to user-friendly messages, displays loading states, and handles network failures. The backend included in this demo provides both normal job data and controlled error responses so the complete module can be tested independently."
