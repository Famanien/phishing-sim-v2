# Phishing Simulation System - Sprint 5

## Quick Start Guide

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

## Run Project

### Option 1: One-Click Run (Windows)
Double-click `run_project.bat` in the project folder.

### Option 2: Manual Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python backend/app.py
   ```
3. Open your browser to: http://127.0.0.1:5000

## Project Structure
- `backend/`: Python Flask application logic and API endpoints
- `static/`: CSS styles and JavaScript files
- `templates/`: HTML templates (Dashboard, Login, Quiz)

### Installation

1. **Navigate to the project directory:**
```bash
cd "c:\Users\Windows\Downloads\Automated Phishing Tool\phishing-sim-project"
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Initialize the database:**
```bash
cd backend
python database.py
```

4. **Run the application:**
```bash
python app.py
```

5. **Access the dashboard:**
Open your browser and navigate to: `http://localhost:5000`

---

## Sprint 5 Features

### ✅ Completed Start-Up Manager Tasks

#### Step 2: Campaign Status and Run Dates
- ✅ Database schema with scheduling fields
- ✅ Campaign status tracking (scheduled/active/completed)
- ✅ Start date and end date support

#### Step 3: Auto-Launch Function
- ✅ Campaign launch automation
- ✅ User segmentation and targeting
- ✅ Automatic message distribution
- ✅ Status management

#### Step 4: Scheduler Mechanism
- ✅ Manual trigger interface ("Run Weekly Simulation")
- ✅ Automated campaign creation
- ✅ Multi-campaign distribution

#### Step 5: Continuous Metrics Tracking
- ✅ Click rate per campaign
- ✅ Report rate per campaign
- ✅ Training completion rate
- ✅ Dashboard visualization
- ✅ Trend comparison

---

## Using the System

### Admin Dashboard

The dashboard has 5 main sections:

1. **Overview** - Dashboard stats and risk distribution
2. **Campaigns** - Create and manage campaigns
3. **Users & Risk** - View user risk categories
4. **Metrics** - Campaign performance and trends
5. **Automation** - Run weekly simulations

### Running a Weekly Simulation

1. Navigate to the **Automation** section
2. Set the week number (default: 5)
3. Click **"Run Weekly Simulation Now"**
4. View results showing:
   - Campaigns launched
   - Messages sent
   - Target users

### Creating a Manual Campaign

1. Navigate to the **Campaigns** section
2. Click **"+ Create Campaign"**
3. Fill in:
   - Campaign name
   - Difficulty (Easy/Medium/Hard)
   - Template
   - Target segment
4. Click **"Create Campaign"**
5. Launch the campaign from the campaigns table

---

## Database Schema

The system uses SQLite with the following tables:

- **users** - User information
- **campaigns** - Campaign definitions with scheduling
- **messages** - Individual phishing messages sent
- **events** - User actions (click, report, training)
- **user_risk** - Risk scores and categories
- **templates** - Phishing email templates
- **campaign_metrics** - Performance tracking

---

## API Endpoints

### Campaigns
- `GET /api/campaigns` - List all campaigns
- `POST /api/campaigns/create` - Create new campaign
- `POST /api/campaigns/<id>/launch` - Launch campaign
- `POST /api/campaigns/<id>/complete` - Complete campaign

### Users
- `GET /api/users` - List all users with risk info
- `POST /api/users/create` - Create new user

### Automation
- `POST /api/automation/run-weekly` - Run weekly simulation

### Metrics
- `GET /api/metrics/all` - All campaign metrics
- `GET /api/metrics/trends` - Trend comparison

---

## File Structure

```
phishing-sim-project/
├── backend/
│   ├── app.py              # Flask application
│   ├── database.py         # Database module
│   ├── automation.py       # Automation logic
│   └── phishing_sim.db     # SQLite database (created on first run)
├── templates/
│   ├── dashboard.html      # Admin dashboard
│   └── training_page.html  # Training page
├── static/
│   ├── dashboard.css       # Dashboard styles
│   └── dashboard.js        # Dashboard JavaScript
├── docs/
│   ├── automation_rules.md # Automation documentation
│   ├── phishing_templates.md
│   ├── risk_register.md
│   └── backlog.md
└── requirements.txt        # Python dependencies
```

---

## Automation Rules

See [automation_rules.md](docs/automation_rules.md) for detailed documentation on:
- Campaign frequency
- User segmentation
- Difficulty strategy
- Training triggers
- Risk scoring

---

## Troubleshooting

### Database not found
Run `python database.py` in the backend directory to initialize.

### Port already in use
Change the port in `app.py`: `app.run(port=5001)`

### Templates not loading
The system seeds initial templates on first run. Refresh the page.

---

## Next Steps (Future Sprints)

- Email integration for real message delivery
- Advanced reporting and PDF export
- User authentication and role-based access
- Scheduled automation (cron/scheduled tasks)
- Mobile app integration

---

*Sprint 5 - Automation & Continuous Campaigns*  
*Start-Up Manager Implementation Complete*
