# Attendance Management System

## Overview
This is a web-based Attendance Management System built with Flask and Pandas. It allows for easy attendance marking, reporting, and dashboard visualization for students. Attendance data is stored in Excel files, and the system provides a simple interface for both marking and reviewing attendance, as well as reporting and resolving issues.

## Features
- Mark attendance by student registration number
- Dashboard with total, present, and absent student counts
- Download daily attendance reports in Excel format
- View student lists and attendance by date
- Report and resolve issues (e.g., room issues)

## Project Structure
```
attend/
├── app.py                # Main Flask application
├── templates/            # HTML templates (Jinja2)
│   ├── index.html
│   ├── dashboard.html
│   ├── students.html
│   ├── download.html
│   └── report.html
├── static/               # Static files (CSS, JS)
│   ├── style.css
│   └── main.js
├── data/                 # Data storage
│   ├── master_list.xlsx  # Master student list
│   ├── issues.xlsx       # Reported issues
│   └── attendance/       # Daily attendance Excel files
└── README.md             # Project documentation
```

## Setup Instructions
1. **Clone the repository**
2. **Install dependencies**
   - Python 3.7+
   - Install required packages:
     ```bash
     pip install flask pandas openpyxl
     ```
3. **Prepare data files**
   - Place your master student list as `data/master_list.xlsx` with columns: `ROLL`, `NAME`, `YEAR`
   - The app will auto-create other files/folders as needed
4. **Run the application**
   ```bash
   python app.py
   ```
5. **Access the web interface**
   - Open your browser and go to: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## Usage
- **Mark Attendance:** Use the scan endpoint or UI to mark attendance by registration number.
- **Dashboard:** View overall stats at `/dashboard`.
- **Download Reports:** Go to `/download-menu` to download daily attendance files.
- **View Students:** See student lists and their attendance at `/students`.
- **Report Issues:** Use `/report` to submit issues (e.g., room problems).

## Data Format
- **Master List:** `data/master_list.xlsx` with columns: `ROLL`, `NAME`, `YEAR`
- **Attendance:** `data/attendance/YYYY-MM-DD.xlsx` with columns: `Reg No`, `Name`, `Class`, `Section`, `Time`
- **Issues:** `data/issues.xlsx` with columns: `Room`, `Issue`, `Reported Time`

## Dependencies
- Flask
- pandas
- openpyxl (for Excel file support)

## License
This project is for educational use. Modify as needed for your institution. 