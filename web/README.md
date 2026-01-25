# FocusOS Frontend

Next.js frontend for FocusOS, built with TypeScript, Tailwind CSS, and Convex.

## Setup

1.  **Install dependencies:**
    ```bash
    cd web
    bun install
    ```

2.  **Initialize Convex:**
    ```bash
    npx convex dev
    ```
    This will prompt you to log in and create a project. It will generate `.env.local` with your deployment URL.

3.  **Run the Agent Service:**
    Ensure the Python agent is running on port 8000:
    ```bash
    cd ../agent
    uvicorn agent.main:app --reload
    ```

4.  **Start Frontend:**
    ```bash
    bun dev
    ```

## Project Structure

- `convex/`: Backend logic and database schema
- `app/`: Next.js App Router pages
- `components/`: UI components
- `lib/agent.ts`: API client for the Python agent
