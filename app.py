from http.server import BaseHTTPRequestHandler, HTTPServer
import mysql.connector
import os

# Function to create the database table if it doesn't exist
def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            original_ip VARCHAR(255) NOT NULL,
            reversed_ip VARCHAR(255) NOT NULL
        )
    ''')
    conn.commit()

def get_client_ip(request_handler):
    # Try to get the client's IP address from X-Forwarded-For header
    client_ip = request_handler.headers.get('X-Forwarded-For')

    # If not found, fall back to using client_address which might be the server IP in some cases
    if not client_ip:
        client_ip = request_handler.client_address[0]

    return client_ip

def get_database_connection():
    # Get database connection parameters from environment variables
    db_host = os.getenv('DB_HOST', 'localhost')
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    db_name = os.getenv('DB_NAME', 'ip_logs_db')

    # Establish database connection
    conn = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

    return conn

# Initialize the table
conn = get_database_connection()
create_table(conn)
conn.close()

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Get the client's IP address
            client_ip = get_client_ip(self)
            
            # Reverse the client's IP address
            reversed_ip = '.'.join(reversed(client_ip.split('.')))
            
            # Log the reversed IP to the database
            log_to_database(client_ip, reversed_ip)
            
            # Send the HTTP response
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(reversed_ip.encode('utf-8'))
            
            # Print to console for debugging
            print(f"Logged reversed IP: {reversed_ip} (Original IP: {client_ip})")

        except Exception as e:
            # Handle any errors
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            error_message = f"Error: {str(e)}"
            self.wfile.write(error_message.encode('utf-8'))
            
            # Print the error to the console for debugging
            print(error_message)

def log_to_database(original_ip, reversed_ip):
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO logs (original_ip, reversed_ip)
        VALUES (%s, %s)
    ''', (original_ip, reversed_ip))
    conn.commit()
    conn.close()

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
