# Cloud Storage Dashboard - Full Stack Application

This project is a complete implementation of the Cloud Storage Dashboard, with a React frontend and a Python (Flask) backend.

## **How to Run This Application**

Critically, this application requires API keys from Google, Dropbox, and Microsoft to function.

### **Step 1: Backend Setup**

1. **Install Python:** Make sure you have Python 3.8 or newer installed.  
2. **Install Dependencies:** Open your terminal, navigate to the project directory, and install the required Python packages using the requirements.txt file.
3. 
   ```
   pip install -r requirements.txt
   ```

4. **Configure API Credentials:**  
   * Open the app.py file.  
   * You will see placeholder values for \*\_CLIENT\_ID and \*\_CLIENT\_SECRET for Google, Dropbox, and OneDrive.  
   * You **MUST** replace these with your own credentials. See the section below on how to get them.  
   * You also need to set a FLASK\_SECRET\_KEY. You can generate one using python \-c 'import os; print(os.urandom(24))'.  
5. **Set Redirect URIs:** In each of your cloud developer consoles, you must add the correct callback/redirect URI so the authentication process works. Add the following URIs for each service:  
   * **Google:** http://127.0.0.1:5000/callback/google  
   * **Dropbox:** http://127.0.0.1:5000/callback/dropbox  
   * **OneDrive:** http://127.0.0.1:5000/callback/onedrive (Set platform to "Web")  
6. **Run the Backend:** In your terminal, run the Flask application.
   ```  
   python app.py
   ```
   The backend server will start on http://127.0.0.1:5000.

### **Step 2: Frontend Access**

1. Open Your Browser: With the backend running, open your web browser and navigate to:  
   http://127.0.0.1:5000  
2. **Use the App:** The Flask server will serve the index.html file, which will load the React application. You can now connect your cloud accounts.

## **How to Get API Credentials**

You need to create an application in the developer console of each cloud provider.

### **Google Drive**

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).  
2. Create a new project.  
3. Go to "APIs & Services" \> "Credentials".  
4. Click "Create Credentials" \> "OAuth client ID".  
5. Select "Web application".  
6. Add http://127.0.0.1:5000 to "Authorized JavaScript origins".  
7. Add http://127.0.0.1:5000/callback/google to "Authorized redirect URIs".  
8. Copy the "Client ID" and "Client Secret" into app.py.  
9. Go to "Library" and enable the **Google Drive API**.

### **Dropbox**

1. Go to the [Dropbox App Console](https://www.dropbox.com/developers/apps).  
2. Click "Create app".  
3. Choose "Scoped Access" and select the permissions you need (e.g., files.metadata.read, sharing.read, account\_info.read). Give your app a name.  
4. In the app's "Settings" tab, add http://127.0.0.1:5000/callback/dropbox as a "Redirect URI".  
5. Copy the "App key" (Client ID) and "App secret" (Client Secret) into app.py.

### **OneDrive (Microsoft)**

1. Go to the [Azure Active Directory admin center](https://entra.microsoft.com/).  
2. Navigate to "Identity" \> "Applications" \> "App registrations".  
3. Click "New registration". Give it a name.  
4. Under "Supported account types," choose "Accounts in any organizational directory... and personal Microsoft accounts".  
5. Under "Redirect URI", select "Web" and enter http://127.0.0.1:5000/callback/onedrive.  
6. Click "Register".  
7. Copy the "Application (client) ID" into app.py.  
8. Go to "Certificates & secrets" \> "New client secret".  
9. Create a new secret, and copy its **Value** (not the ID) into app.py.  
10. Go to "API permissions", click "Add a permission", select "Microsoft Graph", choose "Delegated permissions", and add Files.Read.All, Sites.Read.All, and User.Read.
