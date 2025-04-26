# Deployment Options for TariffDoc AI

This document provides instructions for deploying the TariffDoc AI application using different methods.

## Option 1: Streamlit Cloud (Currently Experiencing Issues)

Streamlit Cloud is the primary deployment platform for this application, but it's currently experiencing issues with blank screens.

1. **Deploy to Streamlit Cloud**:
   - Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
   - Sign in with your GitHub account
   - Connect your repository
   - Select the repository, branch, and main file path (`streamlit_app.py`)
   - Click "Deploy"

2. **Configure Secrets (Optional)**:
   - In your app's settings, go to the "Secrets" section
   - Add your OpenAI API key in TOML format:
     ```toml
     [openai]
     OPENAI_API_KEY = "sk-your-openai-api-key-here"
     OPENAI_MODEL = "gpt-4"
     ```

## Option 2: Static HTML Server (Fallback Option)

If Streamlit Cloud is not working, you can use the static HTML server as a fallback option.

### Local Deployment

1. **Run the Static Server Locally**:
   ```bash
   python serve_static.py
   ```

2. **Access the Application**:
   - Open a browser and navigate to [http://localhost:8000/index.html](http://localhost:8000/index.html)

### Heroku Deployment

1. **Create a Heroku Account**:
   - Sign up at [https://signup.heroku.com/](https://signup.heroku.com/) if you don't have an account

2. **Install the Heroku CLI**:
   - Download and install from [https://devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)

3. **Login to Heroku**:
   ```bash
   heroku login
   ```

4. **Create a New Heroku App**:
   ```bash
   heroku create your-app-name
   ```

5. **Push to Heroku**:
   ```bash
   git push heroku master
   ```

6. **Open the App**:
   ```bash
   heroku open
   ```
   - Append `/index.html` to the URL if needed

## Option 3: Other Deployment Options

### Render

1. **Sign up for Render**:
   - Go to [https://render.com/](https://render.com/) and create an account

2. **Create a New Web Service**:
   - Connect your GitHub repository
   - Set the build command to `pip install -r requirements.txt`
   - Set the start command to `python serve_static.py $PORT`

### Netlify (Static HTML Only)

1. **Sign up for Netlify**:
   - Go to [https://www.netlify.com/](https://www.netlify.com/) and create an account

2. **Deploy from Git**:
   - Connect your GitHub repository
   - Set the build command to empty
   - Set the publish directory to the root directory

3. **Access the Application**:
   - Netlify will provide a URL for your application
   - Append `/index.html` to the URL if needed

## Troubleshooting

If you encounter issues with any deployment method:

1. **Check the Logs**:
   - For Streamlit Cloud: Check the logs in the Streamlit Cloud dashboard
   - For Heroku: Run `heroku logs --tail`
   - For local deployment: Check the terminal output

2. **Verify Dependencies**:
   - Make sure all required dependencies are listed in `requirements.txt`
   - Try running the application locally to ensure it works

3. **Contact Support**:
   - Streamlit Cloud: [https://discuss.streamlit.io/](https://discuss.streamlit.io/)
   - Heroku: [https://help.heroku.com/](https://help.heroku.com/)
