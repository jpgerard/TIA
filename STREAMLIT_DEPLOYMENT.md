# Deploying TariffDoc AI to Streamlit Cloud

This document provides step-by-step instructions for deploying the TariffDoc AI application to Streamlit Cloud.

## Prerequisites

1. A GitHub account with the TariffDoc AI repository
2. A Streamlit Cloud account (sign up at https://streamlit.io/cloud if you don't have one)
3. OpenAI API key (optional, for LLM features)

## Deployment Steps

### 1. Log in to Streamlit Cloud

1. Go to https://streamlit.io/cloud
2. Sign in with your Streamlit account credentials

### 2. Create a New App

1. Click on the "New app" button
2. Connect your GitHub account if you haven't already

### 3. Configure the App

1. Select the repository: `jpgerard/TIA`
2. Select the branch: `master`
3. Set the main file path: `streamlit_app.py`
4. Click "Advanced settings" to configure environment variables

### 4. Configure Environment Variables (Optional)

If you want to enable LLM features, add the following environment variables:

1. `OPENAI_API_KEY`: Your OpenAI API key
2. `OPENAI_MODEL`: The OpenAI model to use (defaults to gpt-4 if not specified)

### 5. Deploy the App

1. Click "Deploy"
2. Wait for the deployment to complete (this may take a few minutes)
3. Once deployed, you'll receive a URL for your application (e.g., https://your-app-name.streamlit.app)

## Post-Deployment

### Updating the App

When you push changes to the GitHub repository, Streamlit Cloud will automatically redeploy your application with the latest changes.

### Monitoring

1. You can monitor your app's usage and logs from the Streamlit Cloud dashboard
2. Click on your app in the dashboard to view details, logs, and settings

### Troubleshooting

If your app fails to deploy or encounters errors:

1. Check the logs in the Streamlit Cloud dashboard
2. Verify that all required files are present in the repository
3. Ensure that the environment variables are correctly set
4. Check that the dependencies in requirements.txt are compatible with Streamlit Cloud

## Additional Resources

- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-cloud)
- [Streamlit Community](https://discuss.streamlit.io/)
- [Streamlit Cloud FAQ](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app/frequently-asked-questions)
