from flask import Flask, request, jsonify, send_from_directory, render_template
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__, static_folder='static')

MASTER_FILE = 'data/master_list.xlsx'
ATTENDANCE_DIR = 'data/attendance'
ISSUES_FILE = 'data/issues.xlsx'

# Create necessary directories and files if they don't exist
os.makedirs('data', exist_ok=True)
os.makedirs(ATTENDANCE_DIR, exist_ok=True)
if not os.path.exists(ISSUES_FILE):
    pd.DataFrame(columns=['Room', 'Issue', 'Reported Time']).to_excel(ISSUES_FILE, index=False)

@app.route('/scan', methods=['POST'])
def scan():
    try:
        reg_no = str(request.json.get('reg_no')).strip()
        print(f"Received reg_no: {reg_no}")
        
        # Load master list
        print(f"Attempting to load master file: {MASTER_FILE}")
        master_df = pd.read_excel(MASTER_FILE)
        print(f"Master file loaded successfully. Shape: {master_df.shape}")
        
        # Validate master list columns
        required_columns = ['ROLL', 'NAME', 'YEAR']
        if not all(col in master_df.columns for col in required_columns):
            print(f"Missing required columns in master list. Found columns: {list(master_df.columns)}")
            return jsonify({'status': 'error', 'message': 'Invalid master list format: Missing required columns'}), 400
            
        master_df['ROLL'] = master_df['ROLL'].astype(str).str.strip()
        student = master_df[master_df['ROLL'] == reg_no]
        
        print(f"Found student: {not student.empty}")
        
        if student.empty:
            return jsonify({'status': 'error', 'message': 'Student not found'}), 404

        # Prepare attendance file
        today = datetime.now().strftime('%Y-%m-%d')
        attendance_file = os.path.join(ATTENDANCE_DIR, f'{today}.xlsx')
        
        try:
            if os.path.exists(attendance_file):
                att_df = pd.read_excel(attendance_file)
                print(f"Attendance file {attendance_file} loaded successfully. Shape: {att_df.shape}")
            else:
                att_df = pd.DataFrame(columns=['Reg No', 'Name', 'Class', 'Section', 'Time'])
                print(f"Attendance file {attendance_file} does not exist. Created empty DataFrame.")
        except Exception as e:
            print(f"Error reading attendance file {attendance_file}: {str(e)}")
            att_df = pd.DataFrame(columns=['Reg No', 'Name', 'Class', 'Section', 'Time'])

        # Mark attendance
        att_df['Reg No'] = att_df['Reg No'].astype(str).str.strip()
        if reg_no in att_df['Reg No'].values:
            print(f"Student {reg_no} already marked in attendance file.")
            return jsonify({'status': 'already_marked'})
        
        student_dict = student.iloc[0].to_dict()
        # Store time in 12-hour format
        current_time = datetime.now().strftime('%I:%M:%S %p')  # e.g., 2:30:22 PM
        new_row = {
            'Reg No': reg_no,
            'Name': student_dict.get('NAME', ''),
            'Class': student_dict.get('YEAR', ''),
            'Section': '',
            'Time': current_time
        }
        att_df = pd.concat([att_df, pd.DataFrame([new_row])], ignore_index=True)
        att_df.to_excel(attendance_file, index=False)
        print(f"Attendance marked for student {reg_no} at {current_time} and saved to {attendance_file}.")
        return jsonify({'status': 'success', 'message': 'Attendance marked successfully'})
    except Exception as e:
        print(f"Scan error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/download/<date>', methods=['GET'])
def download(date):
    filename = f'{date}.xlsx'
    print(f"Attempting to download file: {os.path.join(ATTENDANCE_DIR, filename)}")
    return send_from_directory(ATTENDANCE_DIR, filename, as_attachment=True)

@app.route('/')
def index():
    print("Rendering index page.")
    return render_template('index.html')

@app.route('/download-menu')
def download_menu():
    print(f"Listing files in {ATTENDANCE_DIR}.")
    attendance_files = [f for f in os.listdir(ATTENDANCE_DIR) if f.endswith('.xlsx')]
    attendance_dates = [f.replace('.xlsx', '') for f in attendance_files]
    print(f"Found attendance dates: {attendance_dates}")
    return render_template('download.html', dates=attendance_dates)

@app.route('/dashboard')
def dashboard():
    stats = {
        'total_students': 0,
        'present_today': 0,
        'absent_today': 0
    }
    
    try:
        if not os.path.exists(MASTER_FILE):
            print(f"Master file not found: {MASTER_FILE}")
            return render_template('dashboard.html', stats=stats)
            
        print(f"Loading master file for dashboard: {MASTER_FILE}")
        master_df = pd.read_excel(MASTER_FILE)
        if master_df is None or master_df.empty:
            print("Master file is empty")
            return render_template('dashboard.html', stats=stats)
                
        total_students = len(master_df)
        print(f"Total students in master list: {total_students}")
        
        today = datetime.now().strftime('%Y-%m-%d')
        today_file = os.path.join(ATTENDANCE_DIR, f'{today}.xlsx')
        present_today = 0
        
        if os.path.exists(today_file):
            try:
                att_df = pd.read_excel(today_file)
                if att_df is not None and not att_df.empty:
                    present_today = len(att_df)
                    print(f"Present today: {present_today}")
            except Exception as e:
                print(f"Error reading attendance file for dashboard: {str(e)}")
        
        stats = {
            'total_students': total_students,
            'present_today': present_today,
            'absent_today': max(0, total_students - present_today)
        }
        print(f"Dashboard stats: {stats}")
        return render_template('dashboard.html', stats=stats)
    except Exception as e:
        print(f"Dashboard error: {str(e)}")
        return render_template('dashboard.html', stats=stats)

@app.route('/students')
def students():
    selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    print(f"Accessing students page for date: {selected_date}")
    
    try:
        # Validate master file existence and format
        if not os.path.exists(MASTER_FILE):
            print(f"Master file not found: {MASTER_FILE}")
            return render_template('students.html', grouped_students={}, selected_date=selected_date)
            
        print(f"Loading master file: {MASTER_FILE}")
        master_df = pd.read_excel(MASTER_FILE)
        print(f"Master file loaded. Shape: {master_df.shape}")
        
        if master_df is None or master_df.empty:
            print("Master file is empty")
            return render_template('students.html', grouped_students={}, selected_date=selected_date)
            
        # Validate required columns in master list
        required_columns = ['ROLL', 'NAME', 'YEAR']
        if not all(col in master_df.columns for col in required_columns):
            print(f"Missing required columns in master list. Found columns: {list(master_df.columns)}")
            return render_template('students.html', grouped_students={}, selected_date=selected_date)
            
        # Clean the master list
        master_df['ROLL'] = master_df['ROLL'].astype(str).str.strip()
        master_df['NAME'] = master_df['NAME'].astype(str).str.strip()
        master_df['YEAR'] = master_df['YEAR'].astype(str).str.strip()
        print(f"Master list cleaned. Sample data: {master_df.head(2).to_dict()}")
        
        # Load attendance for the selected date
        attendance_file = os.path.join(ATTENDANCE_DIR, f'{selected_date}.xlsx')
        att_df = None
        if os.path.exists(attendance_file):
            try:
                att_df = pd.read_excel(attendance_file)
                print(f"Attendance file {attendance_file} loaded. Shape: {att_df.shape}")
                # Validate required columns in attendance file
                if not all(col in att_df.columns for col in ['Reg No', 'Time']):
                    print(f"Missing required columns in attendance file. Found columns: {list(att_df.columns)}")
                    att_df = None
                else:
                    att_df['Reg No'] = att_df['Reg No'].astype(str).str.strip()
                    print(f"Attendance file cleaned. Sample data: {att_df.head(2).to_dict()}")
            except Exception as e:
                print(f"Error reading attendance file {attendance_file}: {str(e)}")
                att_df = None
        else:
            print(f"Attendance file {attendance_file} does not exist.")
        
        # Prepare data for the template
        grouped_students = {}
        for _, row in master_df.iterrows():
            year = row['YEAR']
            roll = row['ROLL']
            name = row['NAME']
            
            if year not in grouped_students:
                grouped_students[year] = []
            
            # Check attendance status
            status = "Absent"
            time = None
            if att_df is not None and not att_df.empty:
                # Match ROLL with Reg No
                att_row = att_df[att_df['Reg No'] == roll]
                if not att_row.empty:
                    status = "Present"
                    time = att_row.iloc[0]['Time']  # Time is already in 12-hour format (e.g., 2:30:22 PM)
                    print(f"Student {roll} marked as Present at {time}")
                else:
                    print(f"Student {roll} not found in attendance file, marked as Absent")
            
            grouped_students[year].append({
                'roll': roll,
                'name': name,
                'year': year,
                'status': status,
                'time': time
            })
        
        # Sort students within each year by roll number
        for year in grouped_students:
            grouped_students[year].sort(key=lambda x: x['roll'])
        print(f"Grouped students: { {year: len(students) for year, students in grouped_students.items()} }")
        
        return render_template('students.html', grouped_students=grouped_students, selected_date=selected_date)
        
    except Exception as e:
        print(f"Students page error: {str(e)}")
        return render_template('students.html', grouped_students={}, selected_date=selected_date)

@app.route('/report')
def report():
    print("Rendering report page.")
    try:
        issues_df = pd.read_excel(ISSUES_FILE)
        issues = issues_df.to_dict('records')
        print(f"Loaded issues: {len(issues)}")
        return render_template('report.html', issues=issues)
    except Exception as e:
        print(f"Report page error: {str(e)}")
        return render_template('report.html', issues=[])

@app.route('/add_issue', methods=['POST'])
def add_issue():
    try:
        data = request.json
        room = str(data.get('room')).strip()
        issue = str(data.get('issue')).strip()
        
        if not room or not issue:
            return jsonify({'status': 'error', 'message': 'Room and issue description are required'}), 400
        
        issues_df = pd.read_excel(ISSUES_FILE)
        current_time = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
        new_issue = {
            'Room': room,
            'Issue': issue,
            'Reported Time': current_time
        }
        issues_df = pd.concat([issues_df, pd.DataFrame([new_issue])], ignore_index=True)
        issues_df.to_excel(ISSUES_FILE, index=False)
        print(f"Issue added: {room} - {issue} at {current_time}")
        return jsonify({'status': 'success', 'message': 'Issue reported successfully'})
    except Exception as e:
        print(f"Add issue error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/solve_issue', methods=['POST'])
def solve_issue():
    try:
        data = request.json
        index = int(data.get('index'))
        
        issues_df = pd.read_excel(ISSUES_FILE)
        if index < 0 or index >= len(issues_df):
            return jsonify({'status': 'error', 'message': 'Invalid issue index'}), 400
        
        issues_df = issues_df.drop(index).reset_index(drop=True)
        issues_df.to_excel(ISSUES_FILE, index=False)
        print(f"Issue at index {index} solved")
        return jsonify({'status': 'success', 'message': 'Issue marked as solved'})
    except Exception as e:
        print(f"Solve issue error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)