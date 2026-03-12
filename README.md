# 🏥 College Venue Booking System

A premium, modern web application designed to streamline the process of booking and managing college venues. Built with a focus on sophisticated aesthetics and a seamless user experience.

## 🚀 Key Features

### 👨‍🎓 For Students (CCs)
- **Live Availability**: Instantly check venue availability for specific dates and time slots.
- **Quick Booking**: Integrated "Quick Book" functionality for streamlined reservations.
- **Personal Dashboard**: Track the status of all your booking requests (Pending, Approved, Rejected).
- **Auto-Persistence**: Intelligent form data persistence ensures no information is lost during navigation.

### 👩‍🏫 For Faculty
- **Booking Management**: Review, approve, or reject student booking requests with a single click.
- **Venue Control**: Easily add new venues (Halls, Labs, Seminar Rooms) to the system.
- **Centralized Dashboard**: Oversight of all approved and pending events across the campus.

### 🍱 Advanced UX & Design
- **Single-Page Feel**: Seamless AJAX-based navigation and form submissions for a fluid experience.
- **Premium Aesthetics**: Sophisticated glassmorphism components, custom gradients, and smooth micro-animations.
- **Real-time Feedback**: Global loading states and dynamic slide-in notifications for all actions.

## 🛠️ Technology Stack

- **Backend**: Python / Flask (RESTful architecture)
- **Database**: SQLite (Relational management)
- **Frontend**: Vanilla CSS / JavaScript (Modern ES6+)
- **Security**: Secure session management and PBKDF2 password hashing via `werkzeug`.

## ⚙️ Installation & Setup

### 1. Repository Setup
```bash
git clone https://github.com/iamsurjog/dsw.git
cd dsw
```

### 2. Environment Configuration
**Windows:**
```bash
py -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Running the Application
```bash
flask run
```
The application will be available at `http://127.0.0.1:5000`.

## 📁 Project Structure
- `app.py`: Core application logic and routing.
- `schema.sql`: Database schema definition.
- `static/`: Modern CSS styles and visual assets.
- `templates/`: Modular HTML components and AJAX-ready content fragments.
