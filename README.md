# AMOF — Adaptive Multi-Objective Reasoning Framework

> Production web release of the **AMOF (Adaptive Multi-Objective Reasoning Framework)** user interface, optimized for instant deployment on **Vercel**.

---

## 🚀 Live Deployment on Vercel

This repository contains the standalone, high-performance web build of the AMOF application.

### Zero-Config 1-Click Deployment
1. Import this repository (`haresh27A/amof`) into [Vercel](https://vercel.com/new).
2. Framework Preset: **Other**
3. Root Directory: `./`
4. Build Command: _(leave blank)_
5. Output Directory: _(leave blank)_
6. Click **Deploy**.

Vercel will deploy the site directly to a global Edge CDN in seconds.

---

## 🌟 Key Features

- **💬 AMOF Adaptive Chat**: Intelligent RAG query execution with multi-objective source selection and streaming response generation.
- **⚖️ Side-by-Side Model Comparison**: Compare AMOF routing against standard RAG and direct LLM generation across latency, token cost, and confidence metrics.
- **📚 Enterprise Source Registry**: Manage enterprise data connections, document repositories, and structured databases.
- **📊 Real-Time Benchmarks**: Visual interactive Pareto tradeoffs and performance evaluations.
- **⚙️ Configurable Backend**: Switch or configure the backend API URL directly from the settings dialog within the app.

---

## 🔌 Connecting to Backend API

By default, the web client interacts with the AMOF backend. You can connect your backend:

1. **In-App Configuration**: Open the application in your browser, tap the **Connection / Backend Status** indicator in the navigation bar, and input your hosted backend URL (e.g., `https://your-backend.railway.app` or `http://localhost:8000`).
2. **Build-Time Variable**: Pass `--dart-define=API_BASE_URL=https://your-api.domain.com` when compiling custom Flutter web builds.

---

## 🛠️ Tech Stack & Configuration

- **Frontend**: Flutter Web (CanvasKit / WebAssembly accelerated)
- **Deployment**: Vercel Static Hosting (`vercel.json` SPA routing)
- **Routing**: Clean SPA routing with fallback to `index.html`
- **MIME & Headers**: Pre-configured WebAssembly (`application/wasm`) and immutable asset caching
