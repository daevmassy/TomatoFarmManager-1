# 🍅 Tomato Farm Management System

A comprehensive web-based management system for tomato farming operations, built with HTML/CSS frontend and Python Flask backend.

## 📋 Project Overview

**Problem Statement:**
"Tomato farmers lack a centralized digital system to manage crop lifecycle, resource allocation, and productivity tracking, resulting in inefficiencies and reduced profitability."

**Solution:**
This system provides a complete solution for managing all aspects of tomato farming including planting, harvesting, inventory, operations, and sales tracking.

## 🎯 Objectives

- Develop a web-based system to manage tomato farming operations
- Enable farmers to record and monitor planting, irrigation, fertilization, and harvesting
- Track inventory of farm inputs and labor assignments
- Generate reports on yield, resource usage, and productivity
- Provide a user-friendly interface for data entry and visualization

## 🚀 Features

### Core Modules

1. **🏠 Dashboard**
   - Overview of farm statistics
   - Total plants, harvest, inventory, and sales tracking
   - Recent activity feed

2. **🌱 Planting Management**
   - Register tomato plants with variety, planting date, and location
   - Track expected harvest dates
   - Monitor plant status (Planted, Growing, Flowering, Fruiting)

3. **🧺 Harvesting**
   - Record harvest dates, quantities, and quality grades
   - Link harvests to specific plant records
   - Track harvest by weight or crates

4. **📦 Inventory Management**
   - Track seeds, fertilizers, pesticides, and equipment
   - Set minimum quantity alerts
   - Monitor supplier information

5. **⚙️ Operations Recording**
   - Log farm operations (spraying, weeding, irrigation, fertilizing)
   - Track operation costs and workers
   - Field location mapping

6. **💰 Sales Management**
   - Record sales transactions
   - Track customer information
   - Monitor payment status and revenue

## 💻 Technology Stack

| Component | Technology |
|-----------|-----------|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python 3.11, Flask |
| Database | MySQL |
| Styling | Custom CSS with tomato theme |

## 📁 Project Structure

```
tomato-farm-management/
├── app.py                  # Flask application (main backend)
├── database/
│   └── schema.sql         # MySQL database schema
├── static/
│   ├── css/
│   │   └── style.css      # Custom styling
│   ├── js/
│   │   └── script.js      # Frontend JavaScript
│   └── images/            # Tomato background images
├── templates/
│   ├── base.html          # Base template
│   ├── index.html         # Dashboard
│   ├── planting.html      # Planting management
│   ├── harvesting.html    # Harvest tracking
│   ├── inventory.html     # Inventory management
│   ├── operations.html    # Operations recording
│   └── sales.html         # Sales management
└── README.md              # Project documentation
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11 or higher
- MySQL Server 5.7 or higher
- pip (Python package manager)

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/tomato-farm-management.git
cd tomato-farm-management
```

### Step 2: Install Python Dependencies
```bash
pip install flask flask-cors mysql-connector-python
```

### Step 3: Configure MySQL Database

1. Start your MySQL server
2. Update database credentials in `app.py`:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',          # Your MySQL username
    'password': '',          # Your MySQL password
    'database': 'farmdb'
}
```

### Step 4: Initialize the Database

The application will automatically create the database and tables when you first run it. Alternatively, you can manually import the schema:

```bash
mysql -u root -p < database/schema.sql
```

### Step 5: Run the Application
```bash
python app.py
```

The application will be available at: `http://localhost:5000`

## 📊 Database Schema

The system uses the following MySQL tables:

- **farmers** - Farmer information
- **tomato_plants** - Planting records
- **harvest** - Harvest tracking
- **inventory** - Farm supplies and equipment
- **sales** - Sales transactions
- **operations** - Farm operations (spraying, weeding, irrigation, etc.)
- **spraying** - Pesticide application records
- **weeding** - Weeding activities
- **irrigation** - Irrigation records

## 🎨 Design Features

- **Tomato-themed background** with high-quality images
- **Responsive design** that works on desktop and mobile
- **Modern UI** with gradient colors and smooth transitions
- **Alert system** for low inventory items
- **Real-time statistics** on the dashboard

## 🚧 Limitations

- Requires internet access for full functionality
- Limited to tomato crop management (not multi-crop)
- No integration with IoT sensors or weather APIs (manual data entry)
- Basic security (suitable for local/farm use)

## 🛑 Delimitations

- Focused only on tomato farming lifecycle: planting, growing, harvesting
- Designed for small to medium-sized farms
- Excludes financial accounting and market price tracking
- Only supports English language interface

## 📝 Usage Guide

### Adding a Planting Record
1. Navigate to **Planting** page
2. Select tomato variety
3. Enter planting date and location
4. Submit the form

### Recording a Harvest
1. Navigate to **Harvesting** page
2. Select plant record (optional)
3. Enter harvest date, quantity, and quality
4. Submit the record

### Managing Inventory
1. Navigate to **Inventory** page
2. Add items with category, quantity, and supplier
3. Monitor items highlighted in red (below minimum quantity)

### Recording Operations
1. Navigate to **Operations** page
2. Select operation type (spraying, weeding, irrigation, etc.)
3. Enter date, location, and details
4. Submit the record

### Tracking Sales
1. Navigate to **Sales** page
2. Enter sale date, customer, and quantity
3. Input pricing information
4. Submit the transaction

## 🔮 Future Enhancements

- Integration with weather APIs for climate tracking
- Mobile application for on-field data entry
- Automated reporting with PDF export
- Multi-language support
- Advanced analytics and yield predictions
- IoT sensor integration for real-time monitoring
- Role-based access control for multiple users

## 👨‍💻 Development

### For Visual Studio Code
1. Open the project folder in VS Code
2. Install Python extension
3. Select Python interpreter (3.11+)
4. Run using the integrated terminal

### For phpMyAdmin
1. Access phpMyAdmin in your browser
2. Import `database/schema.sql`
3. View and manage database tables

## 📄 License

This project is open-source and available for educational and commercial use.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📧 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**© 2025 Tomato Farm Management System**
*Manage Your Farm with Excellence*
