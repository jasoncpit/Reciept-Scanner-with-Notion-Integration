Sure! Here's a clean and friendly `README.md` for your **LLM-powered Receipt Scanner API** project, designed for local deployment and Apple Shortcuts integration.

---

# 🧾 J&R Receipt Scanner API

A personal, LLM-powered receipt scanning API built for Jason & Rebekah.
It extracts structured data (items, prices, total, category) from receipt **images or screenshots**, then automatically updates a Notion database.

---

## 🚀 Features

* 🧠 Uses GPT-4 Vision for **OCR and classification**
* 🧾 Extracts items, prices, total, and merchant
* 🗂️ Classifies the receipt into categories like `Grocery`, `Dining`, `Travel`, etc.
* 📚 Automatically adds results to Notion
* ☁️ Deployable to **Railway**

---

## 📁 Project Structure

```
receipt_scanner/
├── app/
│   ├── main.py               # FastAPI app and /scan endpoint
│   ├── llm_handler.py        # GPT-4 Vision: image → JSON
│   ├── notion_client.py      # Writes structured data into Notion DB
│   ├── auth.py               # Simple bearer auth
│   ├── models.py             # Request/response models (Pydantic)
│   └── config.py             # Loads secrets from .env
├── .env.example              # Example environment variables
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker configuration for deployment
├── railway.json              # Railway deployment configuration
├── README.md                 # You are here!
```

---

## ☁️ Deployment to Railway

This project is optimized for deployment on Railway.

### 1. Fork the Repository

Fork this repository to your GitHub account.

### 2. Create a Railway Project

- Go to [Railway](https://railway.app) and create a new project.
- Link your forked GitHub repository.
- Railway will automatically detect the `Dockerfile` and `railway.json` to configure the deployment.

### 3. Configure Environment Variables

In the Railway project settings, add the following environment variables:

```
OPENAI_API_KEY=your_openai_key_here
NOTION_TOKEN=your_notion_integration_token
NOTION_TRANSACTIONS_DATABASE_ID=your_notion_database_id
AUTH_TOKEN=a_very_secret_token
```

### 4. Deploy

Once the environment variables are set, Railway will automatically trigger a deployment. You can monitor the deployment process in the Railway dashboard. After a successful deployment, your API will be available at the public URL provided by Railway.

---

## 🛠️ Local Development

### 1. Clone the repo

```bash
git clone https://github.com/your-username/receipt-scanner.git
cd receipt-scanner
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a `.env` file

Create a `.env` file in the root of the project and add your credentials:

```env
OPENAI_API_KEY=your_openai_key_here
NOTION_TOKEN=your_notion_integration_token
NOTION_TRANSACTIONS_DATABASE_ID=your_notion_database_id
AUTH_TOKEN=a_very_secret_token
```

### 4. Run the FastAPI server

```bash
uvicorn app.main:app --reload
```

---

## 📲 Apple Shortcuts Integration

Create a Shortcut that:

1. Takes or selects a photo
2. Uses `Get Contents of URL` action:

   * Method: `POST`
   * URL: `YOUR_RAILWAY_APP_URL/scan`
   * Headers:
     `Authorization: Bearer YOUR_AUTH_TOKEN`
   * Request Body: `Form` with `file` (image input)

---

## 🛡️ Notes

* Designed for **personal use only**
* Requires internet access (for OpenAI + Notion API)

---

Made with 💙 by Jason & Rebekah
Feel free to fork and adapt for your own life automation setup!



