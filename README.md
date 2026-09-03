## Installation

Activate the virtual environment using the following command:

```bash
poetry shell
```

Install the required packages:

```bash
poetry install
```

## Run

Run the Streamlit application with:

```bash
poetry run streamlit run main.py
```

## Deploy to Streamlit

1. Go to [Streamlit Community Cloud](https://share.streamlit.io/).
2. Create an account or sign in.
3. Click the **"Create app"** button in the top-right corner.
4. Click **"Deploy a public app from GitHub"**.
5. Enter your **Repository** URL.
6. Set the **Main file path** to `main.py`.
7. Click **"Advanced settings"**.

   * Select **Python 3.11** as the Python version.
   * Enter your API key in **Secrets**.
   * Click **"Save"**.
8. Click **"Deploy"**.
