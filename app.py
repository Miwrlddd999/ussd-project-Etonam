from flask import Flask, request, jsonify 
from flask_cors import CORS
from database import db_connect, authenticate_student, get_student_grades
import logging
import re
from cachetools import Cache

app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)

# Cache for storing USSD session states
# maxsize is the size of data the Cache can hold
cache_data = Cache(maxsize=50000)

class UssdState:
    def __init__(self, session_id, msisdn, user_data, network, message, level, step, new_session):
        self.session_id = session_id
        self.msisdn = msisdn
        self.user_data = user_data
        self.network = network
        self.message = message
        self.level = level
        self.step = step
        self.new_session = new_session

@app.route('/ussd', methods=['POST'])
def ussd():
    try:
        # Parse Arkesel USSD request format
        data = request.get_json(silent=True) or {}
        
        session_id = data.get('sessionID', '')
        user_id = data.get('userID', '')
        new_session = data.get('newSession', True)
        msisdn = data.get('msisdn', '')
        user_data = data.get('userData', '')
        network = data.get('network', '')
        
        logging.info(f"USSD Request - Session: {session_id}, New: {new_session}, Data: '{user_data}'")
        
        response = {
            'sessionID': session_id or f"session_{hash(msisdn)}",
            'userID': user_id or msisdn,
            'msisdn': msisdn,
            'continueSession': True,
            'message': ''
        }

        # Menu constants
        WELCOME_MENU = (
            "Welcome to TTU Result Checker\n"
            "1. Check Results\n"
            "2. Exit"
        )
        ENTER_INDEX = "Enter your index number:"
        ENTER_PASSWORD = "Enter your password:"
        SELECT_YEAR = (
            "Select Academic Year:\n"
            "1. Level 100\n"
            "2. Level 200\n"
            "3. Level 300\n"
            "4. Level 400"
        )
        THANK_YOU = "Thank you for using TTU Result Checker."
        INVALID_INPUT = "Invalid input. Please try again."
        NO_RECORD = "No record found for the provided details."

        if new_session:
            # Step 0 - Main menu
            response['message'] = WELCOME_MENU
            response['continueSession'] = True
            
            # Store initial state
            current_state = UssdState(
                session_id=session_id,
                msisdn=msisdn,
                user_data=user_data,
                network=network,
                message=response['message'],
                level=0,
                step=0,
                new_session=True
            )
            
            user_response_tracker = cache_data.get(hash(session_id), [])
            user_response_tracker.append(current_state)
            cache_data[hash(session_id)] = user_response_tracker
            
        else:
            # Get last response from cache
            user_responses = cache_data.get(hash(session_id), [])
            if not user_responses:
                response['message'] = "Session expired. Please try again."
                response['continueSession'] = False
                return jsonify(response)
            
            last_response = user_responses[-1]
            
            user_inputs = []
            for state in user_responses:
                if state.user_data and state.user_data.strip():
                    user_inputs.append(state.user_data.strip())
            
            # Add current input if it's not empty
            if user_data and user_data.strip():
                user_inputs.append(user_data.strip())
            
            logging.info(f"User inputs so far: {user_inputs}")
            logging.info(f"Last response level: {last_response.level}, step: {last_response.step}")
            
            # Process based on current step
            if last_response.level == 0:  # Main menu
                if user_data == "1":
                    # Step 1 - Ask index number
                    response['message'] = ENTER_INDEX
                    response['continueSession'] = True
                    level, step = 1, 1
                elif user_data == "2":
                    # Exit option
                    response['message'] = THANK_YOU
                    response['continueSession'] = False
                    level, step = 0, 0
                else:
                    response['message'] = INVALID_INPUT
                    response['continueSession'] = False
                    level, step = 0, 0
                    
            elif last_response.level == 1:  # Getting user details
                if last_response.step == 1:  # After index number
                    response['message'] = ENTER_PASSWORD
                    response['continueSession'] = True
                    level, step = 1, 2
                elif last_response.step == 2:  # After password
                    response['message'] = SELECT_YEAR
                    response['continueSession'] = True
                    level, step = 1, 3
                elif last_response.step == 3:  # After year selection
                    # Process the complete request
                    if len(user_inputs) >= 5:
                        index = user_inputs[2]  # Skip '*928*230#' and '1'
                        password = user_inputs[3]  # Skip '*928*230#' and '1'
                        year_choice = user_inputs[4]  # Skip '*928*230#' and '1'
                        
                        logging.info(f"Attempting authentication - Index: '{index}', Password: '{password}'")
                        
                        student = authenticate_student(index, password)
                        if not student:
                            logging.error(f"Authentication failed for index: '{index}', password: '{password}'")
                            response['message'] = NO_RECORD
                            response['continueSession'] = False
                            return jsonify(response)

                        student_id = student["id"]
                        name = student["name"]

                        # Map year choice to course groups
                        course_groups = {
                            "1": [
                                "Communication Skills", "Information Technology I", "Introduction to Programming Using C++",
                                "Discrete Mathematics", "Entrepreneurship", "Computer Applications", "Introduce to Economics",
                                "African Studies", "Communication Skills II Industrial Attachment", "Programming Using Java",
                                "Information Technology II", "Database Concepts & Technology", "Mathematics & Statistics",
                                "Introduction to Economics II"
                            ],
                            "2": [
                                "Visual Basic Dot Net", "Database Management System (Oracle)", "Web Technology I",
                                "Hardware Technology I", "Networking I", "Introduction to Accounting", "Research Methodology",
                                "Industrial Attachment II", "Hardware Technology II", "Introduction to Software Engineering",
                                "Web Technology II", "Networking II", "Entrepreneurship II", "Introduction to Accounting II",
                                "PHP Programming"
                            ],
                            "3": [
                                "Management Information Systems", "Systems Analysis and Design", "Information Systems Security",
                                "Systems Administration I", "Operating Systems", "E-Commerce", "Systems Administration II",
                                "Computer Graphics", "Information Systems Security II", "Project",
                                "Computer Organization & Architecture"
                            ],
                             "4": [
                                "Pending..."
                            ]
                        }

                        if year_choice not in course_groups:
                            response['message'] = INVALID_INPUT
                            response['continueSession'] = False
                            return jsonify(response)

                        selected_courses = course_groups[year_choice]

                        grades_rows = get_student_grades(student_id, selected_courses)

                        # Format output for USSD
                        if grades_rows:
                            grades_str = "\n".join([f"{row['course_name']}: {row['grade']}" for row in grades_rows])
                            response['message'] = f"{name}\n{grades_str}"
                        else:
                            response['message'] = f"{name}\nNo grades found for selected year."
                            
                        response['continueSession'] = False
                        return jsonify(response)

                    else:
                        response['message'] = INVALID_INPUT
                        response['continueSession'] = False
                        level, step = 0, 0
            else:
                response['message'] = INVALID_INPUT
                response['continueSession'] = False
                level, step = 0, 0
            
            # Store current state if session continues
            if response['continueSession']:
                current_state = UssdState(
                    session_id=session_id,
                    msisdn=msisdn,
                    user_data=user_data,
                    network=network,
                    message=response['message'],
                    level=level,
                    step=step,
                    new_session=False
                )
                
                user_response_tracker = cache_data.get(hash(session_id), [])
                user_response_tracker.append(current_state)
                cache_data[hash(session_id)] = user_response_tracker

    except Exception as e:
        logging.error(f"USSD processing error: {e}")
        response = {
            'sessionID': session_id if 'session_id' in locals() else '',
            'userID': user_id if 'user_id' in locals() else '',
            'msisdn': msisdn if 'msisdn' in locals() else '',
            'continueSession': False,
            'message': "An unexpected error occurred. Please try again later."
        }

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
