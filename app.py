from flask import Flask, request
import uuid
import datetime

app = Flask(__name__)

doctors = {}
appointments = {}

def add_doctor(first, last):
    # unique ID
    # a first name
    # a last name
    d_id = uuid.uuid4()
    new_doctor = {'first': first, 'last': last}
    doctors[str(d_id)] = new_doctor
    return str(d_id)

def add_appt(d_id, first, last, date_string, kind):
    # unique ID
    # patient first name
    # patient last name
    # date & time
    # kind (New Patient or Follow-up)
    # doctor id

    a_id = uuid.uuid4()
    new_appointment = {
        'first': first,
        'last': last,
        'datetime': date_string,
        'kind': kind,
        'doctor': d_id
    }
    appointments[str(a_id)] = new_appointment
    return str(a_id)

def count_appts(d_id, date_time):
    # ideally done through a database query
    count = 0
    for aid in appointments:
        appointment = appointments[aid]
        if 'deleted' in appointment and appointment['deleted']:
            continue
        if str(appointment['doctor']) != d_id:
            continue
        if appointment['datetime'] == date_time:
            count += 1
    
    return count


@app.route('/doctors', methods=['GET'])
def route_doctors():
    # Get a list of all doctors
    return {'doctors': doctors}, 200

def dr_exists(doctor_id):
    if not doctor_id:
        return False
    # check if doctor exists
    if doctor_id in doctors:
        return True
    return False

@app.route('/appointments', methods=['GET', 'POST', 'DELETE'])
def route_appointments():
    if request.method == 'DELETE':
        aid = request.args.get('appointment_id')
        if aid not in appointments:
            return 'Appointment with that ID does not exist', 404
        appointments[aid]['deleted'] = True
        return "Success", 200

    if request.method == 'GET':
        doctor_id = request.args.get('doctor_id')
        if not dr_exists(doctor_id):
            return 'Doctor with that ID does not exist', 404
        
        date_string = request.args.get('datetime')
        try:
            date_time = datetime.datetime.strptime(date_string, "%Y-%m-%d")
        except ValueError:
            return "'datetime' must be in format YYYY-MM-DD", 400

        end_of_day = date_time + datetime.timedelta(days=1)

        appointment_matches = {}

        # ideally this would done through a database query rather than a loop
        for aid in appointments:
            appointment = appointments[aid]
            if 'deleted' in appointment and appointment['deleted']:
                continue
            if str(appointment['doctor']) != doctor_id:
                continue
            if appointment['datetime'] <= date_time:
                continue
            if appointment['datetime'] >= end_of_day:
                continue
            appointment_matches[aid] = appointment

        return {'appointments': appointment_matches}, 200

    if request.method == 'POST':
        doctor_id = request.args.get('doctor_id')
        if not dr_exists(doctor_id):
            return 'Doctor with that ID does not exist', 404

        date_string = request.args.get('datetime')
        try:
            date_time = datetime.datetime.strptime(date_string, "%Y-%m-%d %I:%M %p")
        except ValueError:
            return "'datetime' must be in format YYYY-MM-DD HH:MM am/pm", 400

        if date_time.minute not in [0,15,30,45]:
            return 'Appointment must be on 15 minute interval', 400
        
        # Check how many appointments this doctor has at this time
        if count_appts(doctor_id, date_time) > 2:
            return 'Doctor with this id is fully booked for this time slot', 400

        kind = request.args.get('kind')
        if kind.lower() not in ['new patient', 'follow-up']:
            return "Appointment kind must be either 'New Patient' or 'Follow-up'", 400

        first = request.args.get('first')
        last = request.args.get('last')

        add_appt(doctor_id, first, last, date_time, kind)
        return 'Success', 200

    return 'Success', 200

if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    new_patient = "New Patient"
    followup = "Follow-up"

    # init
    d_id = add_doctor('John', 'Smith')
    print(d_id)
    date_time = datetime.datetime.strptime('2022-11-01 10:30 am', "%Y-%m-%d %I:%M %p")
    add_appt(d_id, 'Claude', 'Mann', date_time, followup)
    date_time = datetime.datetime.strptime('2022-11-01 11:30 am', "%Y-%m-%d %I:%M %p")
    add_appt(d_id, 'Jamie', 'McMillan', date_time, followup)

    add_doctor('Dave', 'Kent')
    add_doctor('Alice', 'Waller')
    add_doctor('Dottie', 'Myer')

    app.run()