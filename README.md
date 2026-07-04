# PHLMS - Personal Health and Lifestyle Management System

## Setup Instructions

1.  **Environment**: 
    The project is set up in `d:\phlm`.
    A virtual environment `venv` is created and dependencies are installed.

2.  **Database**:
    Database is initialized and migrations are applied.
    Superuser created: `admin` / `adminpass`.

3.  **Running the Server**:
    Run the following command in the terminal:
    ```bash
    venv\Scripts\python.exe manage.py runserver
    ```

4.  **Accessing the System**:
    - Open your browser at `http://127.0.0.1:8000/`.
    - You will see the **Animated Home Page**. Click "Login" to access the system.

## Workflow

### 1. Superuser (System Admin)
- Go to `http://127.0.0.1:8000/admin/`.
- Login with `admin` / `adminpass`.
- **Create a Hospital**:
    - First create a User (e.g., `city_hospital_admin`), check `is_hospital_admin`.
    - Then create a Hospital entry linked to this user.

### 2. Hospital Admin
- Login with the Hospital Admin credentials.
- You will be redirected to the **Hospital Dashboard**.
- Use the dashboard to **Add Doctors** and **Add Patients**.
- **Note**: When creating users, use unique usernames.

### 3. Doctors & Patients
- Login with the credentials created by the Hospital Admin.
- **Change Password**: recommended on first login via the top-right dropdown menu.
- Doctors see appointments and lab reports.
- Patients can book appointments and view their history.

## Project Structure
- `phlms_project/`: Django settings and configuration.
- `core/`: Main app.
    - `models.py`: Database tables (User, Hospital, Doctor, Patient, etc.).
    - `views.py`: Logic for dashboards, home page, and auth.
    - `templates/core/`: HTML using Bootstrap 5 for the UI.
"# django_phlm" 
