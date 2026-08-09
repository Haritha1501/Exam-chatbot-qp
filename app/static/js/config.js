// Configuration for API requests.
// When deployed separately on Vercel, set API_BASE_URL to your deployed Render backend URL.
// Example: window.API_BASE_URL = 'https://exam-bot-backend.onrender.com';
// When running locally or hosted together, keep it empty string ''.

window.API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? ''
    : 'https://YOUR-RENDER-BACKEND-NAME.onrender.com'; // Replace with your Render URL after creating Render Web Service
