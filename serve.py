import http.server
import socketserver
import webbrowser
import os

# Set the port number for the server
PORT = 8000

# Define the handler to be used by the server
Handler = http.server.SimpleHTTPRequestHandler

# Get the current working directory
web_dir = os.path.join(os.path.dirname(__file__), '.')
os.chdir(web_dir)

# Create the server
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")

    # The URL to open in the browser
    url = f"http://localhost:{PORT}"

    # Check if index.html exists and open it
    if os.path.exists("index.html"):
        webbrowser.open_new_tab(url)
    else:
        print("No index.html found, opening the directory view.")
        webbrowser.open_new_tab(url)


    try:
        # Keep the server running until you press Ctrl+C
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping the server.")
        httpd.shutdown()
