# ThesisTrack-Final-Project

ThesisTrack is a role-based web application designed to manage final year university projects. It streamlines communication between students, supervisors, and administrators while providing tools for submission, feedback, attendance tracking, and project monitoring.

---

## 🟦 Overview

ThesisTrack provides a centralized platform for managing the full lifecycle of student projects, from proposal submission to final evaluation. The system ensures efficient collaboration, transparency, and accountability.

---

## 🟩 Features

### Student
- ✅ Secure login
- ✅ Submit project proposals
- ✅ Upload project chapters (Docx)
- ✅ View supervisor feedback
- ✅ Track project progress/status
- ✅ View attendance records
- ✅ Receive notifications (approvals, feedback, deadlines)
- ❌ Cannot register themselves
- ❌ Cannot access other users' data

### Supervisor
- ✅ Secure login
- ✅ View assigned students and projects
- ✅ Approve/reject project proposals
- ✅ Provide feedback on submissions
- ✅ Monitor student progress
- ✅ Manage attendance
- ✅ Communicate with students
- ❌ Cannot create users
- ❌ Cannot access admin-level controls

### Administrator
- ✅ Full system access
- ✅ Create and manage users (students & supervisors)
- ✅ Assign supervisors to students
- ✅ Schedule project defenses
- ✅ Generate reports
- ✅ Manage projects, submissions, and deadlines
- ✅ Monitor supervisor attendance

---

## 🟨 Role-Based Access Control

The system uses Role-Based Access Control (RBAC) with three roles:

- STUDENT  
- SUPERVISOR  
- ADMIN  

Each role has restricted access to specific features and data.

---

## 🟧 Tech Stack

- Backend: Django (Python)
- Frontend: HTML, Tailwind CSS, JavaScript
- Database: SQLite
- Authentication: Django Auth (Custom User Model)

---

## 🟥 Project Structure

```
ThesisTrack/
│
├── accounts/        # Authentication & user roles
├── dashboard/       # Role-based dashboards
├── projects/        # Proposals, submissions, feedback
├── attendance/      # Attendance tracking
├── notifications/   # Alerts & updates
├── core/            # Shared templates & utilities
│
├── templates/       # Global templates (base, layout)
├── static/          # CSS, JS, images
├── media/           # Uploaded files (Docx)
│
├── config/          # Django project settings
├── db.sqlite3       # Database
├── manage.py
```

---

## 🟦 Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/SourTik/thesistrack
cd thesistrack
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create superuser (Admin)
```bash
python manage.py createsuperuser
```

### 6. Run the server
```bash
python manage.py runserver
```

---

## 🟨 Authentication Rules

- Only ADMIN can create users  
- Students and Supervisors cannot register  
- All users log in through a single login page  
- Users are redirected based on role after login  

---

## 🟧 File Upload Rules

- Only `.docx` files are allowed for project submissions  

---

## 🟩 System Highlights

- ✅ Fast performance (2–3 second load time)
- ✅ Secure authentication and authorization
- ✅ Responsive design (mobile & desktop)
- ✅ Clean and maintainable architecture
- ✅ Scalable structure for future expansion

---

## 🟦 System Requirements

- Python 3.x  
- Django  
- SQLite  
- Modern web browser  

---

## 🟨 Contributors

- Ahmed Liban Mohamed  
- Saad Ahmed Yusuf  
- Suhayb Abdirahman Omar  
- Mohamed Abdilahi Mohamed  
- Mustafe Osman Ahmed  

---

## 🟧 License

This project is for academic purposes and can be modified as needed.

---

## 🟩 Future Improvements

- Email notifications  
- Real-time chat system  
- File versioning  
- Advanced analytics dashboard  
- Deployment (Docker / Cloud)  

---

## 🟦 Acknowledgment

This system was developed as a university project to improve thesis management efficiency and communication between students and supervisors.
