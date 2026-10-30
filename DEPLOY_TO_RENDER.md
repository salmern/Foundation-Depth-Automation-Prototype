# Deploy a public demo on Render

This project deploys as two Render web services: a FastAPI backend and a Next.js frontend. The Blueprint is in `render.yaml`.

## Before you deploy

- Keep the GitHub repository **private**. The Render app itself will be public, but the repository does not need to be.
- The app currently has no login. Anyone with the public URL can create projects, upload files, and remove uploaded files. Deploy only if you are comfortable with that access.
- The backend stores data on local disk. The free Render filesystem is temporary; project records, uploads, and generated reports can disappear after a restart, redeploy, or spin-down. Free services also sleep after 15 minutes without traffic and can take about a minute to wake.
- Do not upload client drawings or workbooks unless you have approval to put them on a public service.

## Steps

1. Create a **private GitHub repository** for this `foundation-mvp` folder and push the project files. The `.gitignore` excludes local virtual environments, project data, and archived uploads.
2. In Render, choose **New → Blueprint** and connect that repository. Render will read `render.yaml` and create the API and web services.
3. If Render reports that either service name is taken, rename the service in `render.yaml` and update all matching `onrender.com` URLs in the environment variables.
4. Deploy both services. The API health check is `/api/health`; the frontend is the `foundation-depth-web` service URL.
5. Open the frontend URL and make a small demo project. Avoid relying on uploaded files surviving a service restart.

## Updating the demo

Push changes to the connected branch; Render can rebuild both services from the Blueprint. Check the Render deploy logs if either service fails to build. Changing either service name also requires updating the corresponding API URL and CORS origin in `render.yaml`.
