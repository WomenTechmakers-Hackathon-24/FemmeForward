# FemmeForward Educational Platform - Frontend Static Page

Frontend React WebApp for the FemmeForward educational platform. This application provides personalized learning experiences, quiz generation, and progress tracking functionality. This react app can be deployed standalone or included in the FemmeForward Flask App.

## Prerequisites

- React + Vite + TS
- Tailwind CSS
- Firebase Project
- shadcn/ui
- Axios

## Environment Setup

1. Create a `.env` file in the root directory:
```
VITE_API_BASE_URL=URL where backend is deployed e.g. localhost:5000 for dev

Firebase Config Environment
VITE_FIREBASE_API_KEY=
VITE_FIREBASE_AUTH_DOMAIN=
VITE_FIREBASE_PROJECT_ID=
VITE_FIREBASE_STORAGE_BUCKET=
VITE_FIREBASE_MESSAGING_SENDER_ID=
VITE_FIREBASE_APP_ID=
VITE_FIREBASE_MEASUREMENT_ID=
```

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd femmeforward-frontend
```

2. Install dependencies:
```bash
npm install
```

3a. Run the application (standalone)
```bash
npm run dev
```

The server will start on `http://localhost:5173`

3b. Run the application (with Flask)
```bash
npm run build # build react
mkdir -p ../backend/build # Check if flask directory has build folder, create if it doesn't exist
mv dist/* ../backend/build/ # Move static files built by react to flask build directory
cd ../backend # Move to flask directory
pip install -r requirements.txt # Install femme forward flask requirements
python app.py # run app
```
The server will start on `http://localhost:5000`

## Authentication

The WebApp uses Firebase Google SSO. You need to configure your firebase to allow Google Sign-On
