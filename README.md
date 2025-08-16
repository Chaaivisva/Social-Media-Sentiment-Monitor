# Social Media Sentiment Monitor

This project is a full-stack web application built with Python and Django that monitors social media conversations and performs sentiment analysis on them. The application fetches posts from the X (formerly Twitter) and Reddit APIs, processes the text using advanced AI models, and presents the findings in a dynamic and interactive dashboard.

---

### Architecture Diagram
![Uploading Gemini_Generated_Image_6lgr326lgr326lgr.png…]()

### Key Features

* **Automated Data Pipeline:** A scheduled background task, powered by Celery and Redis, automatically fetches new social media posts at regular intervals, ensuring the data is always fresh.
* **Dynamic Keyword Tracking:** Users can define and manage their own keywords and hashtags to monitor specific topics or brands through the Django admin panel.
* **Advanced NLP Analysis:** The application uses pre-trained Hugging Face models to perform sentiment analysis (positive, negative, neutral) and emotion detection (e.g., joy, anger, sadness).
* **Interactive Dashboard:** A responsive dashboard displays real-time insights with data visualizations, including pie charts and bar charts. Users can filter posts by sentiment or emotion and search for specific phrases.
* **Comparative Analysis:** Users can select two different keywords or brands and compare their sentiment side-by-side on a dedicated dashboard view.
* **User Management:** The project includes Django's built-in user authentication system, allowing users to log in, log out, and save a snapshot of their analysis for later access.

---

### Technology Stack

* **Backend:** Python, Django
* **Data & APIs:** X API (via `tweepy`), Reddit API (via `PRAW`), Hugging Face `transformers`
* **Database:** SQLite (default)
* **Asynchronous Tasks:** Celery, Redis
* **Frontend:** HTML5, Tailwind CSS, Chart.js
* **NLP/ML:** `scikit-learn`

---

### Getting Started

To set up and run this project locally, follow these steps.

#### Prerequisites

* Python 3.8+
* A running Redis server
* API credentials for X (Twitter) and Reddit

#### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
    cd your-repo-name
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Set up API credentials:**
    * Create a `.env` file in the root directory.
    * Add your X and Reddit API keys to the file.
        ```
        TWITTER_BEARER_TOKEN='your_twitter_bearer_token'
        REDDIT_CLIENT_ID='your_reddit_client_id'
        REDDIT_CLIENT_SECRET='your_reddit_client_secret'
        REDDIT_USER_AGENT='your_reddit_user_agent'
        ```
    * **Note:** In a production environment, it is highly recommended to use environment variables instead of hardcoding keys in `settings.py`.

4.  **Run migrations:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5.  **Create a superuser:**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Start the services:**
    * In one terminal, start Redis: `redis-server`
    * In a second terminal, start the Celery worker: `celery -A sentiment_project worker --loglevel=info`
    * In a third terminal, start Celery Beat: `celery -A sentiment_project beat --loglevel=info`
    * In a fourth terminal, start the Django web server: `python manage.py runserver`

The application will now be running at `http://127.0.0.1:8000`. You can add keywords and manage settings from the admin panel at `http://127.0.0.1:8000/admin/`.


Working Model  - [https://www.loom.com/share/6274a7f94f284e33833037619bfb4841?t=174&sid=b5a5ca83-2d88-49e5-92bb-fa5b8e631394]


### USING DOCKER

    * Run the command docker-compose up --build -d
    * Run the container, If there is No data there Apply this command [docker-compose exec web python manage.py fetch_data].
