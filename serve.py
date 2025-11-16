from flask import Flask, jsonify, render_template_string
import http.server
import socketserver
import threading
import webbrowser

# --- Configuration ---
# Port for the web-based control panel
CONTROL_PORT = 8080
# Port for the static website you are serving
WEBSITE_PORT = 8000

# --- Global variables to manage the server state ---
server_thread = None
httpd = None

# --- Create the Flask application for the control panel ---
app = Flask(__name__)

# --- Server Control Functions ---
def start_file_server():
    """Starts the static file server in a new thread."""
    global httpd, server_thread
    if server_thread is None or not server_thread.is_alive():
        # Define a simple handler that serves files from the current directory
        Handler = http.server.SimpleHTTPRequestHandler
        # Create the server instance
        httpd = socketserver.TCPServer(("", WEBSITE_PORT), Handler)
        
        # Start the server in a separate daemon thread
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        print(f"File server started on http://localhost:{WEBSITE_PORT}")
        return True
    return False

def stop_file_server():
    """Stops the static file server thread."""
    global httpd, server_thread
    if httpd and server_thread and server_thread.is_alive():
        print("Shutting down file server...")
        httpd.shutdown()
        httpd.server_close()
        server_thread = None
        httpd = None
        print("File server stopped.")
        return True
    return False

# --- Web Interface (Routes for Flask) ---

@app.route('/')
def control_panel():
    """Renders the main control panel page."""
    # This uses an f-string to embed HTML directly.
    # For larger projects, you would use separate HTML template files.
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Server Control</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                   display: flex; justify-content: center; align-items: center; height: 100vh;
                   background-color: #f0f2f5; margin: 0; }
            .container { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                         text-align: center; }
            h1 { margin-top: 0; }
            #status { margin: 1rem 0; padding: 0.8rem; border-radius: 4px; font-weight: bold; }
            .status-running { background-color: #e8f5e9; color: #2e7d32; }
            .status-stopped { background-color: #ffcdd2; color: #c62828; }
            button { padding: 0.8rem 1.5rem; border: none; border-radius: 4px; font-size: 1rem; cursor: pointer;
                     margin: 0.5rem; transition: background-color 0.2s; }
            #startBtn { background-color: #4CAF50; color: white; }
            #startBtn:hover { background-color: #45a049; }
            #stopBtn { background-color: #f44336; color: white; }
            #stopBtn:hover { background-color: #e53935; }
            .links a { display: block; margin-top: 1rem; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Local Server Control</h1>
            <div id="status">Checking status...</div>
            <button id="startBtn">Start Server</button>
            <button id="stopBtn">Stop Server</button>
            <div class="links">
                <a href="http://localhost:{{ website_port }}" target="_blank">Open Website (Port {{ website_port }})</a>
            </div>
        </div>
        <script>
            const statusDiv = document.getElementById('status');
            const startBtn = document.getElementById('startBtn');
            const stopBtn = document.getElementById('stopBtn');

            async function updateStatus() {
                const response = await fetch('/status');
                const data = await response.json();
                statusDiv.textContent = data.message;
                if (data.running) {
                    statusDiv.className = 'status-running';
                } else {
                    statusDiv.className = 'status-stopped';
                }
            }

            startBtn.addEventListener('click', async () => {
                await fetch('/start', { method: 'POST' });
                updateStatus();
            });

            stopBtn.addEventListener('click', async () => {
                await fetch('/stop', { method: 'POST' });
                updateStatus();
            });

            // Initial status check
            updateStatus();
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template, website_port=WEBSITE_PORT)

@app.route('/start', methods=['POST'])
def start_route():
    if start_file_server():
        return jsonify(success=True, message="Server started.")
    return jsonify(success=False, message="Server is already running.")

@app.route('/stop', methods=['POST'])
def stop_route():
    if stop_file_server():
        return jsonify(success=True, message="Server stopped.")
    return jsonify(success=False, message="Server is not running.")

@app.route('/status')
def status_route():
    is_running = server_thread is not None and server_thread.is_alive()
    if is_running:
        message = f"Server is RUNNING on port {WEBSITE_PORT}"
    else:
        message = "Server is STOPPED"
    return jsonify(running=is_running, message=message)

# --- Main Execution ---
if __name__ == '__main__':
    print("--- Local Server Control Panel ---")
    print(f"Open your browser and navigate to http://localhost:{CONTROL_PORT}")
    print("Use the web page to start and stop your static file server.")
    # Open the control panel automatically
    webbrowser.open(f"http://localhost:{CONTROL_PORT}")
    # Run the Flask app
    app.run(port=CONTROL_PORT)
