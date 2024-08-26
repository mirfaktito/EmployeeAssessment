from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import psycopg2
from urllib.parse import parse_qs

# Koneksi ke database
def connect_db():
    conn = psycopg2.connect(
        dbname="employee_evaluation",
        user="postgres",
        password="13Maret2099",
        host="localhost",
        port="5432"
    )
    return conn

# Ambil data penilaian dari database
def get_evaluations():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM evaluations")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# Simpan data penilaian karyawan ke database
def save_evaluation(data):
    conn = connect_db()
    cur = conn.cursor()
    query = """
    INSERT INTO evaluations (employee_name, employee_id, position, responsibility, timeliness, quality, quantity, attendance, teamwork, initiative, leadership, behavior, character, total_score, grade)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cur.execute(query, (
        data['employee_name'], data['employee_id'], data['position'],
        data['responsibility'], data['timeliness'], data['quality'],
        data['quantity'], data['attendance'], data['teamwork'],
        data['initiative'], data['leadership'], data['behavior'],
        data['character'], data['total_score'], data['grade']
    ))
    conn.commit()
    cur.close()
    conn.close()

# Memperbarui data penilaian karyawan di database
def update_evaluation(data):
    conn = connect_db()
    cur = conn.cursor()
    query = """
    UPDATE evaluations
    SET employee_name = %s, position = %s, responsibility = %s, timeliness = %s, quality = %s, quantity = %s,
        attendance = %s, teamwork = %s, initiative = %s, leadership = %s, behavior = %s, character = %s,
        total_score = %s, grade = %s
    WHERE employee_id = %s
    """
    cur.execute(query, (
        data['employee_name'], data['position'], data['responsibility'], data['timeliness'],
        data['quality'], data['quantity'], data['attendance'], data['teamwork'],
        data['initiative'], data['leadership'], data['behavior'], data['character'],
        data['total_score'], data['grade'], data['employee_id']
    ))
    conn.commit()
    cur.close()
    conn.close()

# Menghapus data
def delete_evaluation(employee_id):
    conn = connect_db()
    cur = conn.cursor()
    query = "DELETE FROM evaluations WHERE employee_id = %s"
    cur.execute(query, (employee_id,))
    conn.commit()
    cur.close()
    conn.close()

# Ambil data penilaian berdasarkan ID
def get_evaluation(employee_id):
    conn = connect_db()
    cur = conn.cursor()
    query = "SELECT * FROM evaluations WHERE employee_id = %s"
    cur.execute(query, (employee_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return {
            'employee_name': row[1],
            'employee_id': row[2],
            'position': row[3],
            'responsibility': row[4],
            'timeliness': row[5],
            'quality': row[6],
            'quantity': row[7],
            'attendance': row[8],
            'teamwork': row[9],
            'initiative': row[10],
            'leadership': row[11],
            'behavior': row[12],
            'character': row[13],
            'total_score': row[14],
            'grade': row[15]
        }
    else:
        return None

# Hitung total nilai dan grade
def calculate_grade(scores):
    total_score = sum(scores.values())
    if total_score >= 80:
        grade = "Baik Sekali"
    elif total_score >= 66:
        grade = "Baik"
    elif total_score >= 56:
        grade = "Cukup"
    elif total_score >= 40:
        grade = "Kurang"
    else:
        grade = "Gagal"
    return total_score, grade

#validasi nilai between 0-10
def validate_score(score):
        """ Validates if the score is between 1 and 10 """
        return 0 < score <= 10

class EmployeeEvaluationHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("index.html", "r") as file:
                self.wfile.write(file.read().encode())
        elif self.path == "/fetch_evaluations":
            evaluations = get_evaluations()
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            evaluations_list = [
                {
                    'employee_name': row[1],
                    'employee_id': row[2],
                    'position': row[3],
                    'responsibility': row[4],
                    'timeliness': row[5],
                    'quality': row[6],
                    'quantity': row[7],
                    'attendance': row[8],
                    'teamwork': row[9],
                    'initiative': row[10],
                    'leadership': row[11],
                    'behavior': row[12],
                    'character': row[13],
                    'total_score': row[14],
                    'grade': row[15]
                }
                for row in evaluations
            ]
            self.wfile.write(json.dumps(evaluations_list).encode())
        elif self.path.startswith("/fetch_evaluation"):
            query_components = parse_qs(self.path.split("?")[1])
            employee_id = query_components["employee_id"][0]
            evaluation = get_evaluation(employee_id)
            if evaluation:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(evaluation).encode())
            else:
                self.send_response(404)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"message": "Evaluation not found"}).encode())
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Page not found")

        

    def do_POST(self):
        if self.path == "/evaluate":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_data = parse_qs(post_data.decode('utf-8'))

            data = {
                'employee_name': post_data['employeeName'][0],
                'employee_id': post_data['employeeID'][0],
                'position': post_data['position'][0],
                'responsibility': int(post_data['responsibility'][0]),
                'timeliness': int(post_data['timeliness'][0]),
                'quality': int(post_data['quality'][0]),
                'quantity': int(post_data['quantity'][0]),
                'attendance': int(post_data['attendance'][0]),
                'teamwork': int(post_data['teamwork'][0]),
                'initiative': int(post_data['initiative'][0]),
                'leadership': int(post_data['leadership'][0]),
                'behavior': int(post_data['behavior'][0]),
                'character': int(post_data['character'][0]),
            }

             # Validate scores
            for key in ['responsibility', 'timeliness', 'quality', 'quantity', 'attendance', 'teamwork', 'initiative', 'leadership', 'behavior', 'character']:
                if not validate_score(data[key]):
                    self.send_response(400)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(f"Invalid input: {key.capitalize()} must be between 1 and 10.".encode())
                    return
                
            

            scores = {
                'responsibility': data['responsibility'],
                'timeliness': data['timeliness'],
                'quality': data['quality'],
                'quantity': data['quantity'],
                'attendance': data['attendance'],
                'teamwork': data['teamwork'],
                'initiative': data['initiative'],
                'leadership': data['leadership'],
                'behavior': data['behavior'],
                'character': data['character'],
            }

            total_score, grade = calculate_grade(scores)
            data['total_score'] = total_score
            data['grade'] = grade

            # Mengecek apakan untuk memasukan data baru atau edit sesuai employee_id
            existing_evaluation = get_evaluation(data['employee_id'])
            if existing_evaluation:
                update_evaluation(data)
                message = f"Evaluation for Employee ID: {data['employee_id']} has been updated successfully."
            else:
                save_evaluation(data)
                message = f"Evaluation for Employee ID: {data['employee_id']} has been added successfully."

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            response = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Evaluation Result</title>
                </head>
                <body>
                    <h1>Evaluation Result</h1>
                    <p>{message}</p>
                    <p>Name: {data['employee_name']}</p>
                    <p>Position: {data['position']}</p>
                    <p>NIK: {data['employee_id']}</p>
                    <h2>Nilai</h2>
                    <p>Responsibility: {data['responsibility']}</p>
                    <p>Timeliness: {data['timeliness']}</p>
                    <p>Quality: {data['quality']}</p>
                    <p>Quantity: {data['quantity']}</p>
                    <p>Attendance: {data['attendance']}</p>
                    <p>Teamwork: {data['teamwork']}</p>
                    <p>Initiative: {data['initiative']}</p>
                    <p>Leadership: {data['leadership']}</p>
                    <p>Behavior: {data['behavior']}</p>
                    <p>Character: {data['character']}</p>
                    <h2>Total Score: {data['total_score']}</h2>
                    <h2>Grade: {data['grade']}</h2>
                    <a href="/">Back to Form</a>
                </body>
                </html>
            """
            self.wfile.write(response.encode())
        
    #Fungsi menghapus data
    def do_DELETE(self):
        if self.path.startswith("/delete_evaluation"):
            query_components = parse_qs(self.path.split("?")[1])
            employee_id = query_components.get("employee_id", [None])[0]

            if employee_id:
                delete_evaluation(employee_id)
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                response = f"""
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Deletion Result</title>
                    </head>
                    <body>
                        <h1>Deletion Result</h1>
                        <p>Evaluation for Employee ID: {employee_id} has been deleted successfully.</p>
                        <a href="/">Back to Form</a>
                    </body>
                    </html>
                """
                self.wfile.write(response.encode())
            else:
                self.send_response(400)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"Bad Request: Missing employee_id")
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Page not found")

def run(server_class=HTTPServer, handler_class=EmployeeEvaluationHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
