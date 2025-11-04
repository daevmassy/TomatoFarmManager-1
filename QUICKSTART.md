# Quick Start Guide

## For GitHub Upload

This project is ready to upload to GitHub and use in Visual Studio!

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: Tomato Farm Management System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/tomato-farm-management.git
git push -u origin main
```

### Step 2: Clone on Your Computer

```bash
git clone https://github.com/YOUR_USERNAME/tomato-farm-management.git
cd tomato-farm-management
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up MySQL Database

**Using XAMPP (Easiest):**
1. Install XAMPP from https://www.apachefriends.org/
2. Start MySQL and Apache in XAMPP Control Panel
3. Open http://localhost/phpmyadmin
4. Go to Import tab
5. Select `database/schema.sql` file
6. Click "Go"

**See MYSQL_SETUP.md for more detailed instructions**

### Step 5: Run the Application

```bash
python app.py
```

Open your browser to: http://localhost:5000

## Features

✅ **Home Dashboard** - View farm statistics and recent activities
✅ **Planting** - Register and manage tomato plants
✅ **Harvesting** - Record harvest data with quality grades
✅ **Inventory** - Track seeds, fertilizers, and equipment
✅ **Operations** - Log farm operations (spraying, weeding, irrigation)
✅ **Sales** - Manage sales transactions and revenue

## Project Structure

```
📁 tomato-farm-management/
├── 📄 app.py                  # Flask backend application
├── 📁 database/
│   └── 📄 schema.sql         # MySQL database schema
├── 📁 static/
│   ├── 📁 css/
│   │   └── 📄 style.css      # Tomato-themed styling
│   ├── 📁 js/
│   │   └── 📄 script.js      # Frontend JavaScript
│   └── 📁 images/            # Tomato background images
├── 📁 templates/             # HTML templates
│   ├── 📄 base.html
│   ├── 📄 index.html
│   ├── 📄 planting.html
│   ├── 📄 harvesting.html
│   ├── 📄 inventory.html
│   ├── 📄 operations.html
│   └── 📄 sales.html
├── 📄 requirements.txt       # Python dependencies
├── 📄 README.md             # Full documentation
├── 📄 MYSQL_SETUP.md        # MySQL setup guide
└── 📄 QUICKSTART.md         # This file
```

## Using in Visual Studio Code

1. Open VS Code
2. File → Open Folder → Select `tomato-farm-management`
3. Install Python extension
4. Open terminal (Ctrl+`)
5. Run: `pip install -r requirements.txt`
6. Run: `python app.py`
7. Click the localhost link or open http://localhost:5000

## Troubleshooting

**Can't connect to database?**
- Make sure MySQL is running (XAMPP Control Panel)
- Verify the schema is imported in phpMyAdmin
- Check credentials in `app.py` (default: user='root', password='')

**See MYSQL_SETUP.md for detailed troubleshooting**

## Need Help?

Check these files:
- `README.md` - Complete project documentation
- `MYSQL_SETUP.md` - MySQL installation and setup
- `database/schema.sql` - Database structure

Enjoy managing your tomato farm! 🍅
