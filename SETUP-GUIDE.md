# ProcureAI — Setup Guide (For New Users)

## What is ProcureAI?
A local AI-powered procurement assistant that can:
- Search your entire computer for files
- Analyze quotations, invoices, and purchase orders
- Compare vendors and track price history
- Organize folders and draft emails

Everything runs **on your machine** — your files never leave your laptop.

---

## Step 1: Install Docker Desktop

1. Go to: https://www.docker.com/products/docker-desktop/
2. Download **Docker Desktop for Windows**
3. Install it (follow the wizard — accept all defaults)
4. **Restart your computer** when prompted
5. Open Docker Desktop and wait until it says **"Docker Desktop is running"**

> ⚠️ If you see "WSL 2 installation is incomplete", follow the link Docker provides to install the WSL 2 kernel update.

---

## Step 2: Get a DeepSeek API Key (Free)

1. Go to: https://platform.deepseek.com/
2. Create a free account
3. Go to **API Keys** → Create a new key
4. Copy the key (starts with `sk-...`)

---

## Step 3: Set Up the App

1. Copy the entire **"Purchase Agent"** folder to your computer (e.g., `D:\Purchase Agent\`)

2. Open the `.env` file in the folder with Notepad and replace the API key:
   ```
   DEEPSEEK_API_KEY=sk-YOUR_KEY_HERE
   ```
   Save and close.

3. (Optional) If you want email features, add your Gmail credentials:
   ```
   GMAIL_USER=your.email@gmail.com
   GMAIL_APP_PASSWORD=your_app_password
   ```

---

## Step 4: Run the App

**Option A — Double-click (Easy)**
- Double-click `start-app.bat`
- Wait ~30 seconds for first-time setup
- Your browser will open automatically to http://localhost:3000

**Option B — Command Line**
- Open Terminal/PowerShell in the folder
- Run: `docker-compose up --build`
- Open http://localhost:3000 in your browser

---

## Step 5: Stop the App

- Double-click `stop-app.bat`
- Or run `docker-compose down` in the terminal

---

## Daily Usage

| Action | How |
|--------|-----|
| **Start** | Double-click `start-app.bat` |
| **Stop** | Double-click `stop-app.bat` |
| **Use** | Open http://localhost:3000 |

Your data (quotes, vendor history) is saved in the `memory/` folder and persists between restarts.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Docker is not running" | Open Docker Desktop and wait for it to start |
| "Port 3000 is in use" | Close any other app using port 3000, or change the port in `docker-compose.yml` |
| First run is slow | Normal! Docker downloads ~2GB of base images on first run. Subsequent starts are instant. |
| API errors | Check your DeepSeek API key in `.env` and ensure you have credits |

---

## Important Notes for Your Friend

1. **The `.env` file contains YOUR API key** — your friend needs their OWN DeepSeek key
2. **The `memory/` folder** contains your procurement data — don't share it unless intended
3. **First run takes 2-5 minutes** as Docker builds the containers. After that, starts take ~10 seconds
4. **Disk access**: The app can read files on D: drive and the user's Desktop/Documents/Downloads
