# TeamUps

**TeamUps** is a Django-based team collaboration platform that helps users form balanced teams, manage tasks, send invitations, rate teammates, and get real-time notifications.

It uses a simple ML model (K-Nearest Neighbors) to predict a user’s personality type from their skills, helping create more complementary teams.

## Features

- **User Profiles**
  - Custom user model with bio, avatar, skills, availability status, and rating
  - Character types: `Leader`, `Supporter`, `Thinker`, `Doer`, `Connector`
  - ML-powered character type prediction from skills

- **Teams**
  - Create teams (with optional leadership invitation)
  - Invite / remove members
  - Team size limit and teamwork score
  - Leadership transfer via special invitations

- **Tasks**
  - Create tasks linked to teams
  - Task types: Planning, Creative, Technical, Research, Testing
  - Status tracking (Pending / Completed)
  - Extend deadlines

- **Invitations & Notifications**
  - Regular member invitations + Leadership invitations
  - Real-time notifications via Django Channels + Redis (WebSockets)
  - In-app notification list

- **Ratings**
  - Rate other users (only if you share a team)
  - Rate teams
  - Running average scores for both users and teams

- **REST API**
  - Full CRUD via Django REST Framework for Users, Teams, Tasks, Invitations, and Notifications
  - Extra endpoints for toggling availability and extending deadlines

- **Other**
  - Password reset via email
  - Account deletion with confirmation
  - Docker support (PostgreSQL + Redis)
  - WhiteNoise for static files

## Tech Stack

| Layer              | Technology                          |
|--------------------|-------------------------------------|
| Backend            | Django 5.2 + Django REST Framework  |
| Real-time          | Django Channels + Redis             |
| Database           | PostgreSQL (SQLite for local)       |
| ML                 | scikit-learn (KNeighborsClassifier) |
| Frontend           | Django Templates + Custom CSS       |
| Deployment         | Docker + Gunicorn + WhiteNoise      |

## Project Structure

```
TeamUps/
├── main/                    # Main application
│   ├── learning_model/      # ML model + training script
│   ├── static/main/         # CSS + logos
│   ├── templates/main/      # HTML templates
│   ├── models.py            # User, Team, Task, Invitation, etc.
│   ├── views.py             # Class-based views
│   ├── interfaces.py        # DRF ViewSets + API views
│   ├── forms.py
│   ├── consumers.py         # WebSocket consumer
│   └── ...
├── teamups/                 # Project settings
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── manage.py
```

## Getting Started

### Prerequisites

- Python 3.12+
- Docker & Docker Compose (recommended)
- PostgreSQL & Redis (if not using Docker)

### 1. Clone the repository

```bash
git clone https://github.com/Emixin/TeamUps.git
cd TeamUps
```

### 2. Environment variables

Create a `.env` file in the root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_PASSWORD=your-postgres-password
EMAIL_HOST_PASSWORD=your-gmail-app-password
REDIS_HOST=127.0.0.1
```

### 3. Run with Docker (recommended)

```bash
docker-compose up --build
```

The app will be available at: **http://localhost:8000**

Services started:
- `web` → Django (port 8000)
- `db` → PostgreSQL (port 5433)
- `redis` → Redis (port 6379)

### 4. Run locally (without Docker)

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Update settings.py DATABASES HOST to 'localhost' if needed
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 5. Retrain the ML model (optional)

```bash
cd main/learning_model
python train.py
```

> Note: The training script currently points to a hardcoded Windows path. Update it to use your local `db.sqlite3` or PostgreSQL connection.

## API Endpoints

Base URL: `/api/`

| Resource            | Endpoint                         | Notes    |
|---------------------|----------------------------------|----------|
| Users               | `/api/users/`                    | ViewSet  |
| Teams               | `/api/teams/`                    | ViewSet  |
| Tasks               | `/api/tasks/`                    | ViewSet  |
| Invitations         | `/api/invitations/`              | ViewSet  |
| Notifications       | `/api/notifications/`            | ViewSet  |
| Toggle Availability | `/api/user/`                     | POST     |
| Extend Deadline     | `/api/extend_deadline/<pk>/`     | POST     |

## Character Types

The system predicts one of these types based on the user’s skills:

- **Leader** – Organizes and directs
- **Supporter** – Helps and encourages
- **Thinker** – Analyzes and strategizes
- **Doer** – Executes and delivers
- **Connector** – Networks and communicates

## License

This project is currently unlicensed.
Feel free to contact the author for collaboration.

---

Made by Emixin(https://github.com/Emixin)
