# Python HTTP Server with CGI Support

This Python script sets up a basic HTTP server capable of serving static files and executing CGI scripts written in Python.

## Features

- **Static File Serving:** Handles and serves static files like HTML, images, and text.
- **Directory Listing:** Displays the contents of directories when accessed.
- **CGI Execution:** Executes Python scripts with a `.py` extension as CGI scripts.

## Prerequisites

- **Python 3.x:** Ensure that Python 3 is installed on your system. You can download it from the [official Python website](https://www.python.org/).

## Installation

No external packages are required for this script as it utilizes Python's standard library modules. Simply ensure you have Python 3 installed.

## Usage

1. **Save the Script:**
   - Save the provided code in a file named `server.py`.

2. **Prepare Your Content:**
   - Place your static files and Python CGI scripts in the same directory as `server.py` or in its subdirectories.

3. **Run the Server:**
   - Open a terminal or command prompt.
   - Navigate to the directory containing `server.py`.
   - Execute the server with the command:
     ```bash
     python server.py
     ```
   - The server will start and listen on `localhost` at port `8000`.

4. **Access the Server:**
   - Open a web browser.
   - Navigate to `http://localhost:8000/` to view your served content.

## Notes

- **CGI Scripts:** Ensure your Python CGI scripts have the `.py` extension and proper permissions to be executed by the server.
- **Port Configuration:** The server is set to run on port `8000`. To change this, modify the following line in the script:
  ```python
  server = HTTPServer(('localhost', 8000), Handler)
