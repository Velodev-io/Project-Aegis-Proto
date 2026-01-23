# Aegis Prototype Setup Instructions

## 1. Backend (Python)
This handles the Sentinel (AI), Advocate (Playwright), and Database.

1.  **Navigate to backend**:
    ```bash
    cd aegis_proto/backend
    ```
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    playwright install
    ```
3.  **Run the Server**:
    ```bash
    python main.py
    ```
    *Server runs at http://0.0.0.0:8000*

## 2. Global Steward Dashboard (Web)
This is the "Control Center" for the Human-in-the-Loop.

1.  **Open a new terminal**.
2.  **Navigate to frontend_web**:
    ```bash
    cd aegis_proto/frontend_web
    ```
3.  **Install & Run**:
    ```bash
    npm install
    npm run dev
    ```
    *Open the provided Local URL (e.g., http://localhost:5173).*
    *Use the toggle in the top nav to switch between "Senior Mode" (Demo) and "Steward Mode".*

## 3. Senior Mobile App (Flutter)
This is the "Project Aegis" mobile interface.

1.  **Open a new terminal**.
2.  **Navigate to frontend_assets**:
    ```bash
    cd aegis_proto/frontend_assets
    ```
3.  **Initialize Flutter Project**:
    Since this folder currently contains just the source code, generate the platform files:
    ```bash
    flutter create . --org com.aegis.prototype
    ```
4.  **Configure Permissions (Important for Voice)**:
    *   **iOS (`ios/Runner/Info.plist`)**: Open this file and add:
        ```xml
        <key>NSMicrophoneUsageDescription</key>
        <string>Aegis needs the mic to protect you from scams.</string>
        <key>NSSpeechRecognitionUsageDescription</key>
        <string>Aegis needs to hear callers to identify fraud.</string>
        ```
    *   **Android (`android/app/src/main/AndroidManifest.xml`)**: Add:
        ```xml
        <uses-permission android:name="android.permission.RECORD_AUDIO" />
        <uses-permission android:name="android.permission.INTERNET"/>
        ```
5.  **Run the App**:
    ```bash
    flutter run
    ```
    *Note: Verify `lib/api_service.dart` points to your backend IP/localhost.*

## 4. Testing the Flows
1.  **Scam Protection**: In the Mobile App, tap the Shield (or use Sim button) and say "Analyze this call". The Sentinel will analyze the mock transcript. If "Scam" is detected, the Red Warning Overlay appears.
2.  **Bill Automation**: Say/Click "Check Bills". The Advocate (Playwright) will check the `mock_portal.html`.
    - Since the mock bill ($145.50) > Limit ($100), it will match as **Suspicious**.
    - The Mobile App will say "Steward Notified".
3.  **HITL Oversight**: Go to the **Web Dashboard**. You will see the new "Pending Approval".
    - Click "Approve" or "Reject".
    - The status is updated in the Trust Vault.

## 5. Troubleshooting & Fallbacks
- **"Command not found: flutter"**:
  - If you haven't installed the Flutter SDK, **don't worry!**
  - The **Web Dashboard** (Step 2) includes a **"Senior Mode"**.
  - Open the web app, and use the navigation at the top to switch to "Senior Mode". This fully simulates the Mobile App experience (Shield, Voice Buttons, Scam Alerts) right in your browser.
  - To install Flutter later, visit: [flutter.dev/docs/get-started/install/macos](https://flutter.dev/docs/get-started/install/macos)

- **Backend Connection**: If running on a physical phone, ensure `lib/api_service.dart` uses your Mac's LAN IP (e.g., `192.168.1.X`), not `localhost`.
- **OpenAI Key**: If you want real AI analysis, set `export OPENAI_API_KEY=sk-...` before running the backend. Otherwise, it uses the mock logic.
