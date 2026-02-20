# Automation Rules - Sprint 5

## Overview
This document defines the automation policy for continuous phishing simulation campaigns. The system supports automated campaign scheduling, user segmentation, and targeted training delivery.

---

## Campaign Frequency

### Weekly Cadence
- **Standard Frequency:** 1 campaign per week for all users
- **High-Risk Frequency:** +1 additional targeted campaign per week
- **Scheduling:** Campaigns run on-demand via admin trigger (simulating weekly automation)

---

## Audience Strategy

### User Segmentation
The system automatically segments users into risk categories based on their behavior:

| Segment | Criteria | Campaign Frequency |
|---------|----------|-------------------|
| **All Users** | Everyone in the system | 1 campaign/week |
| **High Risk** | Risk score ≥ 7 | 2 campaigns/week |
| **Medium Risk** | Risk score 3-6 | 1 campaign/week |
| **Low Risk** | Risk score ≤ 2 | 1 campaign/week |

### Target Selection Rules
- **All Users Campaign:** Sent to every registered user
- **High-Risk Campaign:** Only sent to users with "High" risk category
- **Medium-Risk Campaign:** Only sent to users with "Medium" risk category
- **Low-Risk Campaign:** Only sent to users with "Low" risk category

---

## Difficulty Strategy

### Progressive Difficulty
Campaigns are assigned difficulty levels based on the target audience and week:

| Week | All Users | High-Risk Users |
|------|-----------|-----------------|
| Week 5 | Medium | Hard |
| Week 6 | Medium | Hard |
| Week 7+ | Medium/Hard | Hard |

### Difficulty Definitions
- **Easy:** Basic phishing indicators, obvious red flags
- **Medium:** Realistic scenarios with subtle indicators
- **Hard:** Highly sophisticated, minimal red flags

---

## Training Strategy

### Automatic Training Triggers

#### Click Event
- **Action:** User clicks phishing link
- **Response:** Training becomes **mandatory**
- **Content:** Redirect to training page with educational content
- **Tracking:** Event logged as `training_started`

#### Repeat Click
- **Criteria:** User clicks phishing link 2+ times across simulations
- **Response:** Extra quiz required
- **Tracking:** User marked as "repeat offender"
- **Additional Action:** Flagged for manager review

#### Report Event
- **Action:** User reports phishing email
- **Response:** Positive reinforcement message
- **Impact:** Risk score decreases by 2 points

---

## Risk Scoring System

### Scoring Rules
| Event | Score Change |
|-------|--------------|
| Click phishing link | +3 points |
| Report phishing email | -2 points |
| Ignore email | 0 points |
| Repeat click (same week) | +2 extra points |
| Failed training quiz | +2 points |
| Completed training | 0 points |

### Risk Categories
| Category | Score Range | Color Code |
|----------|-------------|------------|
| Low Risk | 0-2 | 🟢 Green |
| Medium Risk | 3-6 | 🟡 Yellow |
| High Risk | 7+ | 🔴 Red |

### Repeat Offender Criteria
A user is marked as a **repeat offender** if:
- They click phishing links **2 or more times** across different simulations
- OR they click once **after completing training**

---

## Automation Workflow

### Weekly Simulation Process

1. **Trigger:** Admin clicks "Run Weekly Simulation"
2. **Campaign Creation:**
   - System creates Medium difficulty campaign for all users
   - System creates Hard difficulty campaign for high-risk users (if any exist)
3. **User Selection:**
   - Query database for target users based on segmentation rules
   - Apply risk category filters
4. **Message Distribution:**
   - Create message record for each target user
   - Mark campaign as "active"
5. **Metrics Initialization:**
   - Initialize campaign metrics tracking
   - Set baseline counters to 0
6. **Result Reporting:**
   - Display number of campaigns launched
   - Show total messages sent
   - List campaign details

---

## Campaign Lifecycle

### Status Flow
```
scheduled → active → completed
```

### Status Definitions
- **Scheduled:** Campaign created but not yet launched
- **Active:** Campaign is running, users can interact
- **Completed:** Campaign finished, metrics finalized
- **Paused:** Campaign temporarily stopped (future feature)

---

## Metrics Tracking

### Real-Time Metrics
The system tracks the following metrics for each campaign:

- **Total Sent:** Number of messages distributed
- **Click Rate:** Percentage of users who clicked the phishing link
- **Report Rate:** Percentage of users who reported the email
- **Training Completion Rate:** Percentage who completed training after clicking

### Trend Analysis
The system compares:
- Baseline campaign vs. latest campaign
- Click rate trends (should decrease over time)
- Report rate trends (should increase over time)
- High-risk group performance vs. general population

---

## Implementation Notes

### Manual Trigger (Current Implementation)
For coursework demonstration purposes, the automation uses a **manual trigger**:
- Admin clicks "Run Weekly Simulation" button
- System executes all automation rules
- Results displayed immediately

This simulates what would be a scheduled cron job or automated task in a production environment.

### Future Enhancements
- Scheduled execution using Python `schedule` library or cron
- Email integration for actual message delivery
- Advanced segmentation based on department, role, or custom criteria
- A/B testing for template effectiveness
- Automated reporting to stakeholders

---

## Safety & Ethics

### Simulation-Only Notice
⚠️ **IMPORTANT:** This is a simulation tool for educational purposes only.

- No real emails are sent
- No real user data is collected
- All phishing links are simulated
- Clear "simulation only" messaging throughout

### Data Protection
- User data stored locally in SQLite database
- No external data transmission
- Risk scores used only for educational improvement
- Transparent tracking and reporting

---

## Success Criteria

### Week 5 Goals
- ✅ Automated campaign creation and distribution
- ✅ User segmentation by risk category
- ✅ Metrics tracking for all campaigns
- ✅ Trend comparison functionality
- ✅ Manual trigger for weekly simulation

### Expected Outcomes
- Decreased click rates over time
- Increased report rates over time
- Improved awareness among high-risk users
- Measurable behavior change

---

*Document Version: 1.0*  
*Last Updated: Sprint 5*  
*Owner: Start-Up Manager*
