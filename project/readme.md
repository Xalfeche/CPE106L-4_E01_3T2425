
# CommunityConnect

  

## Project Description

  

CommunityConnect is a ride-sharing application designed to connect riders with available drivers. It features a backend API built with FastAPI for handling ride requests, managing pending rides, and providing analytics. The frontend is a desktop application built with Flet, offering interfaces for riders to request rides, drivers to accept pending rides, and administrators to view ride statistics. The application utilizes MongoDB for data storage and Google Maps API for distance and duration calculations.

  

## Setup Instructions

  

### Prerequisites

  

* Python 3.8+

  

* MongoDB installed and running (default port 27017)

  

* Google Maps API Key (replace Insert your own API key here in backend.py with your actual key; you might also need to enable the Distance Matrix API for your key)

  

### Ubuntu Virtual Machine (VM) Setup

  

1. **Update System Packages:**

  

```
sudo apt update

sudo apt upgrade -y
```

  

2. **Install Python and pip:**

  

```
sudo apt install python3 python3-pip -y
```

  

3. **Install MongoDB:**

Follow the official MongoDB installation guide for Ubuntu: <https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/>

A simplified version for quick setup:

  

```
sudo apt-get install gnupg curl -y

curl -fsSL [https://www.mongodb.org/static/pgp/server-7.0.asc](https://www.mongodb.org/static/pgp/server-7.0.asc) | \

sudo gpg -o /usr/share/keyrings/mongodb-archive-keyring.gpg \

--dearmor

echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-archive-keyring.gpg ] [https://repo.mongodb.org/apt/ubuntu](https://repo.mongodb.org/apt/ubuntu) jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

sudo apt-get update

sudo apt-get install -y mongodb-org

sudo systemctl start mongod

sudo systemctl enable mongod
```

  

4. **Clone the Repository (or copy files):**

Copy the main.py, backend.py, frontend.py, and requirements.txt files into a directory on your VM.

  

5. **Install Python Dependencies:**

Navigate to the project directory and install the required Python packages:

  

```
pip3 install -r requirements.txt
```

  

### Windows Terminal Setup

  

1. **Install Python:**

Download and install Python from the official website: <https://www.python.org/downloads/>

Make sure to check "Add Python to PATH" during installation.

  

2. **Install MongoDB:**

Download and install MongoDB Community Server from the official website: <https://www.mongodb.com/try/download/community>

Follow the installation wizard. Ensure MongoDB is running as a service.

  

3. **Copy Project Files:**

Copy the main.py, backend.py, frontend.py, and requirements.txt files into a directory on your Windows machine.

  

4. **Install Python Dependencies:**

Open Windows Terminal (or Command Prompt/PowerShell), navigate to the project directory, and install the required Python packages:

  

```
pip install -r requirements.txt
```

  

## How to Run the Application

  

Once all dependencies are installed and MongoDB is running, you can run the application using the main.py script. This script will start both the FastAPI backend and the Flet frontend.

  

1. **Open your terminal (Ubuntu VM) or Windows Terminal (Windows).**

  

2. **Navigate to the directory where you saved the project files.**

  

```
cd path/to/your/project
```

  

3. **Run the application:**

  

```
python main.py
```

  

This will:

  

* Start the FastAPI backend on http://127.0.0.1:8000.

  

* Launch the Flet desktop application, which will connect to the backend.

  

## Dependencies and Installation Steps

  

The Python dependencies are listed in requirements.txt:

  

* fastapi: Web framework for the backend API.

  

* uvicorn: ASGI server to run the FastAPI application.

  

* motor: Asynchronous Python driver for MongoDB.

  

* flet: Framework for building desktop applications with Python.

  

* requests: HTTP library for making requests to the backend API from the frontend.

  

* googlemaps: Python client for Google Maps Platform APIs.

  

* matplotlib: Plotting library for generating analytics charts (used in the admin panel).

  

These dependencies are installed via pip using the requirements.txt file as described in the setup instructions.

  

## Team Members and Roles

  

* **Alfeche**: Backend Development, API Design, Database Integration

  

* **Mataac**: Frontend Development, UI/UX Design