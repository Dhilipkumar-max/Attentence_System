function markAttendance() {
    const regNo = document.getElementById('reg_no_input').value;
    fetch('/scan', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({reg_no: regNo})
    })
    .then(res => res.json())
    .then(data => {
        showResult(data.status === 'success' ? 'Attendance marked successfully!' : 
                  data.status === 'already_marked' ? 'Attendance already marked for today' : 
                  data.message || 'Error marking attendance', 
                  data.status === 'success' ? 'success' : 'error');
        if (data.status === 'success') {
            document.getElementById('reg_no_input').value = '';
            document.getElementById('scanned-result').textContent = '';
            document.getElementById('reg_no_input').focus();
        }
    });
}

function downloadAttendance() {
    const date = document.getElementById('date_picker').value;
    if (!date) {
        alert('Please select a date');
        return;
    }
    window.location.href = `/download/${date}`;
}

function addIssue() {
    const room = document.getElementById('room_input').value;
    const issue = document.getElementById('issue_input').value;
    if (!room || !issue) {
        showResult('Please enter both room number and issue description', 'error');
        return;
    }

    fetch('/add_issue', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({room, issue})
    })
    .then(res => res.json())
    .then(data => {
        showResult(data.message, data.status === 'success' ? 'success' : 'error');
        if (data.status === 'success') {
            document.getElementById('room_input').value = '';
            document.getElementById('issue_input').value = '';
            setTimeout(() => location.reload(), 1000); // Reload to show new issue
        }
    });
}

function solveIssue(index) {
    if (!confirm('Are you sure you want to mark this issue as solved?')) return;

    fetch('/solve_issue', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({index})
    })
    .then(res => res.json())
    .then(data => {
        showResult(data.message, data.status === 'success' ? 'success' : 'error');
        if (data.status === 'success') {
            setTimeout(() => location.reload(), 1000); // Reload to update table
        }
    });
}

function showResult(message, type) {
    const resultDiv = document.getElementById('result');
    if (resultDiv) {
        resultDiv.textContent = message;
        resultDiv.className = `result-message ${type}`;
        setTimeout(() => {
            resultDiv.className = 'result-message';
        }, 3000);
    }
}