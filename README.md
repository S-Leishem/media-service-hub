# Media Downloader

A free, open-source web application that allows users to download content from YouTube and Instagram. Simply paste a link to a YouTube video, YouTube Shorts, Instagram Reel, or Instagram post and download it in your preferred quality.

## Features

- ✅ Download YouTube Videos & Shorts
- ✅ Download Instagram Reels & Posts
- ✅ Multiple quality options
- ✅ Beautiful, modern UI
- ✅ Responsive design (works on mobile and desktop)
- ✅ No ads or tracking
- ✅ Fast and efficient

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python Flask
- **Download Engine**: yt-dlp
- **CORS**: Flask-CORS for cross-origin requests

## Project Structure

```
video-downloder/
├── frontend/
│   ├── index.html       # Main HTML file
│   ├── style.css        # Styling
│   └── script.js        # Frontend logic
└── backend/
    ├── app.py           # Flask application
    ├── requirements.txt # Python dependencies
    └── .env.example     # Environment variables example
```

## Local Setup & Running

### Prerequisites

- Python 3.8 or higher
- Node.js (optional, for local frontend development)
- pip (Python package manager)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy environment file:
```bash
cp .env.example .env
```

5. Run the Flask server:
```bash
python app.py
```

The backend will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Start a local server (choose one):

**Using Python:**
```bash
python -m http.server 8000
```

**Using Node.js (http-server):**
```bash
npm install -g http-server
http-server
```

3. Open your browser and visit `http://localhost:8000`

## API Endpoints

### GET /health
Health check endpoint to verify the server is running.

**Response:**
```json
{"status": "ok"}
```

### POST /api/info
Fetch media information without downloading.

**Request:**
```json
{
  "url": "https://www.youtube.com/watch?v=..."
}
```

**Response:**
```json
{
  "url": "https://www.youtube.com/watch?v=...",
  "title": "Video Title",
  "duration": 300,
  "upload_date": "20231215",
  "thumbnail": "https://...",
  "platform": "YouTube",
  "formats": [
    {
      "format_id": "22",
      "quality": "720p",
      "resolution": "1280x720",
      "format": "mp4",
      "filesize": "25000000"
    }
  ],
  "ext": "mp4"
}
```

### POST /api/download
Download media in the specified format.

**Request:**
```json
{
  "url": "https://www.youtube.com/watch?v=...",
  "format_id": "22"
}
```

**Response:**
File download stream

## Free Hosting Options

### Option 1: Vercel + Render (Recommended)

**Frontend on Vercel (Free):**
1. Push your frontend code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Sign up with GitHub
4. Click "New Project" and select your repository
5. Set root directory to `frontend`
6. Deploy (it's automatic!)
7. Update `API_BASE_URL` in `script.js` to your Render URL

**Backend on Render (Free):**
1. Push your backend code to GitHub
2. Go to [render.com](https://render.com)
3. Sign up and create a new Web Service
4. Connect your GitHub repository
5. Set build command: `pip install -r requirements.txt`
6. Set start command: `python app.py`
7. Deploy!
8. Your backend URL will be provided (e.g., `https://your-app.onrender.com`)

### Option 2: Railway.app (Free tier available)

**Both Frontend & Backend:**
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Create a new project
4. Deploy your code
5. Railway handles everything automatically

### Option 3: PythonAnywhere (Backend only)

**Backend on PythonAnywhere (Free tier):**
1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Sign up for free account
3. Upload your backend code
4. Configure Flask app
5. Set web address
6. Run your app
7. **Frontend**: Deploy to Vercel (see Option 1)

### Option 4: Heroku Alternative with Railway or Render

Both services have replaced Heroku's free tier and offer better free plans:
- Railway: $5 credit monthly (more than enough for small projects)
- Render: Truly free tier with some limitations

## Step-by-Step Deployment Guide

### Deploy to Vercel + Render (Complete Guide)

#### Step 1: Prepare Your GitHub Repository

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/video-downloder.git
git push -u origin main
```

#### Step 2: Deploy Backend to Render

1. Create account on [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Select your GitHub repository
4. Fill in the details:
   - **Name**: media-downloader-api
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Branch**: main
5. Click "Create Web Service"
6. Wait for deployment to complete
7. Copy your service URL (e.g., `https://media-downloader-api.onrender.com`)

#### Step 3: Deploy Frontend to Vercel

1. Create account on [vercel.com](https://vercel.com)
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Settings:
   - **Framework Preset**: Other
   - **Root Directory**: `frontend`
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)
5. Click "Deploy"

#### Step 4: Update Frontend API URL

After deployment, update your frontend's `API_BASE_URL`:

Edit `frontend/script.js` (line 1):
```javascript
const API_BASE_URL = 'https://media-downloader-api.onrender.com'; // Your Render URL
```

Push the changes:
```bash
git add frontend/script.js
git commit -m "Update API URL for production"
git push
```

Vercel will auto-redeploy with the new URL.

### Environment Variables

For production, you should set environment variables:

**In Render/Railway:**
1. Go to your service settings
2. Add environment variables
3. Example variables:
   ```
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```

## Troubleshooting

### Issue: CORS Errors
**Solution**: Make sure the backend URL in `frontend/script.js` matches your deployed backend URL.

### Issue: Download fails
**Solution**: 
- Check internet connection
- Try a different URL
- Make sure yt-dlp is up to date (run `pip install --upgrade yt-dlp`)

### Issue: Render/Railway app goes to sleep
**Solution**: 
- Use Render's paid plan ($7/month) for always-on
- Keep the app active by making requests periodically
- Consider upgrading to a better hosting solution

### Issue: File size limits
**Solution**: 
- Most platforms support files up to 100GB
- For very large files, stream directly instead of downloading

## Usage Tips

- **Copy Link**: Copy the link to your clipboard and paste it in the app
- **Multiple Downloads**: You can queue multiple downloads
- **Background Download**: Don't close the browser tab during download
- **File Location**: Check your Downloads folder for downloaded files

## Legal Notice

- This tool is for personal use only
- Respect copyright and intellectual property rights
- Don't download copyrighted content without permission
- Some platforms may have terms of service restrictions on downloading
- Use responsibly!

## Contributing

Found a bug or have a feature request? Feel free to open an issue or submit a pull request!

## License

This project is open source and available under the MIT License.

## Support

Need help? Check the troubleshooting section or open an issue on GitHub!

---

**Happy downloading!** 🎉

For questions or issues, create an issue on GitHub or contact the maintainers.
