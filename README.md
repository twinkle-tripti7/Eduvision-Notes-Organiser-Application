# Eduvision-Notes-Organiser-Application

##65 Many times, while studying or attending a lecture, students take screenshots of important slides, notes, or code snippets, intending to organize them later. However, these images often get lost in a cluttered phone gallery.
## EduVision was built to solve this problem by providing a structured way to store images under categories, search them easily, and even edit them without the hassle of manual organization.


## ✨ Features  

✅ **Organized Storage** – Save and categorize images under custom tags like **"Math," "AI Notes," or "Code Snippets"** for **easy retrieval** whenever needed.  
✅ **Quick Search** – Instantly find stored screenshots using a **powerful keyword-based search**, so you never lose important notes again.  
✅ **In-App Editing** – Modify stored images **directly within the app** without needing to export them to another tool, making quick edits seamless.  
✅ **One-Click Upload** – Capture screenshots and store them in the app **with just a single tap**, reducing the hassle of manual organization.  
✅ **Easy Cleanup** – No longer need a saved image? **Delete it effortlessly** in just one click, keeping your storage clutter-free.  
✅ **Secure Google Authentication** – All your images and data are **protected using Firebase Authentication**, ensuring that **only you** have access to your stored content.  



# Tech Stack🔧 
## Backend: Flask (Python) – Handles server-side logic and user authentication
## Frontend: HTML & CSS – Provides a clean and structured user interface
## Poppins Font – Ensures a modern and visually appealing design
## Database: SQLite (or any preferred database) – Stores user notes and images
## Other Libraries: Werkzeug – Secures passwords through hashing
## Flask-Login – Manages user sessions and authentication


# Project Structure📂
bash
Copy
Edit
## /static/uploads       # Stores uploaded files  
## /templates/index.html # Main UI for note management  
## auth.py               # Handles authentication & user sessions  
## app.py                # Main Flask application logic  
## models.py             # Database models for storing notes  


# Setup & Installation🔧
1️⃣ Clone the repository
git clone https://github.com/your-username/eduvision-notes-organizer.git
cd eduvision-notes-organizer

2️⃣ Install dependencies
pip install -r requirements.txt

3️⃣ Run the application
python app.py

4️⃣ Open in browser
http://127.0.0.1:5000

🎯 Future Enhancements
📌 OCR Integration – Extract text from images automatically for better searchability
📌 Dark Mode – Enhance accessibility and improve the user experience
📌 Cloud Storage Support – Integrate with Google Drive or OneDrive for seamless access

💡 Contributing
Contributions are welcome! If you’d like to enhance the features, fix bugs, or improve documentation, feel free to fork the repo.



