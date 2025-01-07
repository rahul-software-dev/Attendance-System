from flask import Flask, request, jsonify, render_template
from datetime import datetime
import csv
import os
from geopy.distance import geodesic

app = Flask(__name__)

# Set the geolocation of the class (latitude, longitude)
CLASS_LOCATION = (40.7128, -74.0060)  # Example: Coordinates of New York City
MAX_DISTANCE_KM = 0.5  # Maximum distance from class location to mark attendance

# Load students from the CSV file
STUDENT_FILE = 'students.csv'

def load_students():
    students = {}
    if os.path.exists(STUDENT_FILE):
        with open(STUDENT_FILE, mode='r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)
            for row in csv_reader:
                student_id, name, email = row
                students[email] = {'student_id': student_id, 'name': name}
    return students

# Serve the HTML form
@app.route('/')
def index():
    return render_template('index.html')

# Mark attendance route
@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    students = load_students()
    email = request.form.get('email')
    latitude = request.form.get('latitude', type=float)
    longitude = request.form.get('longitude', type=float)

    if email not in students:
        return jsonify({'error': 'Student not found'}), 404

    student = students[email]
    student_location = (latitude, longitude)

    distance = geodesic(CLASS_LOCATION, student_location).km
    if distance > MAX_DISTANCE_KM:
        return jsonify({'error': 'Not within allowed distance for attendance.'}), 403

    ip_address = request.remote_addr
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with open('attendance.csv', mode='a') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow([student['student_id'], student['name'], email, ip_address, now])

    return jsonify({'message': 'Attendance marked successfully', 'student': student, 'time': now})

# Run the app
if __name__ == '__main__':
    app.run(port=5006)
