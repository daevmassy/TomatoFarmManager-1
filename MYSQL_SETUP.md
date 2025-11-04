# MySQL Setup Guide for Tomato Farm Management System

## Quick Setup Instructions

### Option 1: Using XAMPP (Recommended for Beginners)

1. **Download and Install XAMPP**
   - Download from: https://www.apachefriends.org/
   - Install with MySQL and phpMyAdmin components

2. **Start MySQL Server**
   - Open XAMPP Control Panel
   - Click "Start" next to MySQL
   - Click "Start" next to Apache (for phpMyAdmin)

3. **Import Database Schema**
   - Open browser and go to: http://localhost/phpmyadmin
   - Click "Import" tab
   - Choose file: `database/schema.sql`
   - Click "Go" to execute

4. **Verify Database**
   - You should see "farmdb" database in the left sidebar
   - Click it to see all tables

5. **Run the Application**
   ```bash
   python app.py
   ```
   - Access at: http://localhost:5000

### Option 2: Using Standalone MySQL

1. **Install MySQL Server**
   - Windows: Download from https://dev.mysql.com/downloads/installer/
   - Mac: `brew install mysql`
   - Linux: `sudo apt-get install mysql-server`

2. **Start MySQL Service**
   - Windows: Services → MySQL → Start
   - Mac/Linux: `sudo systemctl start mysql` or `sudo service mysql start`

3. **Import Schema**
   ```bash
   mysql -u root -p < database/schema.sql
   ```

4. **Update Credentials (if needed)**
   - Edit `app.py`, line 12-17:
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'user': 'root',           # Your MySQL username
       'password': 'your_password',  # Your MySQL password
       'database': 'farmdb'
   }
   ```

### Option 3: Using phpMyAdmin (Any Setup)

1. **Access phpMyAdmin**
   - Usually at: http://localhost/phpmyadmin
   - Or: http://localhost:8080/phpmyadmin

2. **Create Database**
   - Click "New" in left sidebar
   - Database name: `farmdb`
   - Click "Create"

3. **Import Schema**
   - Select `farmdb` database
   - Click "Import" tab
   - Choose `database/schema.sql`
   - Click "Go"

4. **Verify Tables**
   - You should see these tables:
     - farmers
     - tomato_plants
     - harvest
     - inventory
     - sales
     - operations
     - spraying
     - weeding
     - irrigation

## Troubleshooting

### Error: "Can't connect to MySQL server"
**Solution:**
- Ensure MySQL service is running
- Check username and password in `app.py`
- Verify MySQL is running on port 3306

### Error: "Access denied for user"
**Solution:**
- Update `DB_CONFIG` in `app.py` with correct credentials
- Default is usually: user='root', password='' (empty)

### Error: "Unknown database 'farmdb'"
**Solution:**
- Import the schema file using phpMyAdmin or command line
- Or manually create database: `CREATE DATABASE farmdb;`

### Tables are empty
**Solution:**
- This is normal! Start adding data through the web interface
- Sample inventory data is auto-populated in schema.sql

## Default Configuration

The application uses these default MySQL settings:
- **Host:** localhost
- **Port:** 3306 (default MySQL port)
- **User:** root
- **Password:** (empty)
- **Database:** farmdb

## Testing the Connection

1. Run the application: `python app.py`
2. Look for: "Database initialized successfully!"
3. If you see errors, check the troubleshooting section above
4. Access the app at: http://localhost:5000

## For Visual Studio Code

1. Open project folder in VS Code
2. Install "Python" extension
3. Install "MySQL" extension (optional, for database browsing)
4. Open terminal in VS Code
5. Run: `python app.py`

## For GitHub

The project is ready to push to GitHub:
```bash
git init
git add .
git commit -m "Initial commit: Tomato Farm Management System"
git branch -M main
git remote add origin https://github.com/yourusername/tomato-farm-management.git
git push -u origin main
```

## Production Deployment

For production use:
1. Use a production WSGI server (Gunicorn, uWSGI)
2. Set strong SESSION_SECRET environment variable
3. Use proper MySQL credentials (not root)
4. Enable SSL/HTTPS
5. Regular database backups

## Support

If you encounter issues:
1. Check MySQL is running
2. Verify credentials in app.py
3. Check firewall allows port 3306
4. Review error messages in terminal
