from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_cors import CORS
import psycopg2
from psycopg2 import pool, extras
from datetime import datetime, timedelta
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'tomato-farm-secret-key-2025')
CORS(app)

# Admin authentication is now done via database

# Decorator to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorator to check if user is admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        if session['user_type'] != 'admin':
            flash('Admin access required for this action', 'error')
            return redirect(request.referrer or url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

DATABASE_URL = os.environ.get('DATABASE_URL')

connection_pool = None

def init_pool():
    global connection_pool
    if DATABASE_URL and not connection_pool:
        try:
            connection_pool = pool.SimpleConnectionPool(1, 10, DATABASE_URL)
            print("Database connection pool created successfully!")
        except Exception as e:
            print(f"Error creating connection pool: {e}")

def get_db_connection():
    try:
        if not connection_pool:
            init_pool()
        if connection_pool:
            return connection_pool.getconn()
        return None
    except Exception as e:
        print(f"Error getting database connection: {e}")
        return None

def release_db_connection(conn):
    if connection_pool and conn:
        connection_pool.putconn(conn)

def init_db():
    try:
        if not DATABASE_URL:
            print("DATABASE_URL not found. Please create a PostgreSQL database in the Database tab.")
            return
        
        connection = get_db_connection()
        if not connection:
            print("Could not connect to database")
            return
            
        cursor = connection.cursor()
        
        with open('database/schema_postgres.sql', 'r') as f:
            sql_script = f.read()
        
        cursor.execute(sql_script)
        
        # Create employee_tasks table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employee_tasks (
                id SERIAL PRIMARY KEY,
                employee_number INTEGER NOT NULL CHECK (employee_number BETWEEN 1 AND 10),
                task_date DATE NOT NULL,
                task_type VARCHAR(100) NOT NULL,
                field_location VARCHAR(200),
                description TEXT NOT NULL,
                start_time TIME,
                estimated_hours DECIMAL(4,1),
                status VARCHAR(50) DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        connection.commit()
        cursor.close()
        release_db_connection(connection)
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        if connection:
            release_db_connection(connection)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login/admin', methods=['POST'])
def login_admin():
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    
    connection = get_db_connection()
    if not connection:
        flash('Database connection error. Please try again.', 'error')
        return redirect(url_for('login'))
    
    try:
        cursor = connection.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        
        if user and user['password'] == password:
            session['user_type'] = 'admin'
            session['username'] = user['full_name'] or 'Admin'
            session['user_email'] = user['email']
            flash(f'Welcome {session["username"]}! You have full access.', 'success')
            release_db_connection(connection)
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
            release_db_connection(connection)
            return redirect(url_for('login'))
    except Exception as e:
        print(f"Login error: {e}")
        flash('Login error. Please try again.', 'error')
        release_db_connection(connection)
        return redirect(url_for('login'))

@app.route('/login/guest', methods=['POST'])
def login_guest():
    session['user_type'] = 'guest'
    session['username'] = 'Employee'
    flash('Welcome Employee! You have view-only access.', 'success')
    return redirect(url_for('index'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_user():
    full_name = request.form.get('full_name', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    # Validation
    if not full_name or not email or not password:
        flash('All fields are required.', 'error')
        return redirect(url_for('register'))
    
    if password != confirm_password:
        flash('Passwords do not match.', 'error')
        return redirect(url_for('register'))
    
    if len(password) < 6:
        flash('Password must be at least 6 characters long.', 'error')
        return redirect(url_for('register'))
    
    connection = get_db_connection()
    if not connection:
        flash('Database connection error. Please try again.', 'error')
        return redirect(url_for('register'))
    
    try:
        cursor = connection.cursor(cursor_factory=extras.RealDictCursor)
        
        # Check if email already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            flash('An account with this email already exists. Please login.', 'error')
            cursor.close()
            release_db_connection(connection)
            return redirect(url_for('login'))
        
        # Insert new user
        cursor.execute("""
            INSERT INTO users (email, password, full_name) 
            VALUES (%s, %s, %s)
        """, (email, password, full_name))
        
        connection.commit()
        cursor.close()
        release_db_connection(connection)
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
        
    except Exception as e:
        print(f"Registration error: {e}")
        flash('Error creating account. Please try again.', 'error')
        if connection:
            release_db_connection(connection)
        return redirect(url_for('register'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    connection = get_db_connection()
    stats = {
        'total_plants': 0,
        'total_harvest': 0,
        'inventory_items': 0,
        'total_sales': 0
    }
    recent_activities = []
    
    if not connection:
        flash('Database not connected. Please create a PostgreSQL database in the Database tab.', 'error')
    
    if connection:
        try:
            cursor = connection.cursor(cursor_factory=extras.RealDictCursor)
            
            cursor.execute("SELECT COUNT(*) as count FROM tomato_plants")
            result = cursor.fetchone()
            stats['total_plants'] = result['count'] if result else 0
            
            cursor.execute("SELECT COALESCE(SUM(quantity), 0) as total FROM harvest WHERE unit = 'kg'")
            result = cursor.fetchone()
            stats['total_harvest'] = float(result['total']) if result else 0
            
            cursor.execute("SELECT COUNT(*) as count FROM inventory")
            result = cursor.fetchone()
            stats['inventory_items'] = result['count'] if result else 0
            
            cursor.execute("SELECT COALESCE(SUM(total_amount), 0) as total FROM sales")
            result = cursor.fetchone()
            stats['total_sales'] = float(result['total']) if result else 0
            
            cursor.execute("""
                SELECT 'Planting' as type, planting_date as date, 
                       variety || ' - ' || quantity || ' plants' as details
                FROM tomato_plants 
                ORDER BY planting_date DESC LIMIT 5
            """)
            recent_activities = cursor.fetchall()
            
            cursor.close()
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            release_db_connection(connection)
    
    return render_template('index.html', stats=stats, recent_activities=recent_activities)

@app.route('/planting')
@login_required
def planting():
    connection = get_db_connection()
    plants = []
    page = request.args.get('page', 1, type=int)
    per_page = 10
    total_items = 0
    
    if connection:
        try:
            cursor = connection.cursor(cursor_factory=extras.RealDictCursor)
            
            # Get total count
            cursor.execute("SELECT COUNT(*) as count FROM tomato_plants")
            result = cursor.fetchone()
            total_items = result['count'] if result else 0
            
            # Get paginated items
            offset = (page - 1) * per_page
            cursor.execute("""
                SELECT * FROM tomato_plants 
                ORDER BY planting_date DESC
                LIMIT %s OFFSET %s
            """, (per_page, offset))
            plants = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            release_db_connection(connection)
    
    total_pages = (total_items + per_page - 1) // per_page
    return render_template('planting.html', plants=plants, page=page, total_pages=total_pages)

@app.route('/planting/add', methods=['POST'])
@admin_required
def add_planting():
    connection = get_db_connection()
    
    if connection:
        try:
            variety = request.form['variety']
            planting_date = request.form['planting_date']
            expected_harvest = request.form.get('expected_harvest', None)
            field_location = request.form.get('field_location', '')
            quantity = request.form.get('quantity', 1)
            status = request.form.get('status', 'Growing')
            notes = request.form.get('notes', '')
            
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO tomato_plants 
                (variety, planting_date, expected_harvest_date, field_location, quantity, status, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (variety, planting_date, expected_harvest, field_location, quantity, status, notes))
            
            connection.commit()
            cursor.close()
            flash('Planting record added successfully!', 'success')
        except Exception as e:
            print(f"Database error: {e}")
            flash('Error adding planting record', 'error')
        finally:
            release_db_connection(connection)
    
    return redirect(url_for('planting'))

@app.route('/planting/delete/<int:id>', methods=['POST'])
@admin_required
def delete_planting(id):
    connection = get_db_connection()
    
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM tomato_plants WHERE id = %s", (id,))
            connection.commit()
            cursor.close()
            flash('Planting record deleted successfully!', 'success')
        except Exception as e:
            print(f"Database error: {e}")
            flash('Error deleting record', 'error')
        finally:
            release_db_connection(connection)
    
    return redirect(url_for('planting'))

@app.route('/harvesting')
@login_required
def harvesting():
    connection = get_db_connection()
    harvests = []
    plants = []
    page = request.args.get('page', 1, type=int)
    per_page = 10
    total_items = 0
    
    if connection:
        try:
            cursor = connection.cursor(cursor_factory=extras.RealDictCursor)
            
            # Get total count
            cursor.execute("SELECT COUNT(*) as count FROM harvest")
            result = cursor.fetchone()
            total_items = result['count'] if result else 0
            
            # Get paginated harvests
            offset = (page - 1) * per_page
            cursor.execute("""
                SELECT h.*, p.variety as plant_variety
                FROM harvest h
                LEFT JOIN tomato_plants p ON h.plant_id = p.id
                ORDER BY h.harvest_date DESC
                LIMIT %s OFFSET %s
            """, (per_page, offset))
            harvests = cursor.fetchall()
            
            cursor.execute("SELECT * FROM tomato_plants ORDER BY planting_date DESC")
            plants = cursor.fetchall()
            
            cursor.close()
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            release_db_connection(connection)
    
    total_pages = (total_items + per_page - 1) // per_page
    return render_template('harvesting.html', harvests=harvests, plants=plants, page=page, total_pages=total_pages)

@app.route('/harvesting/add', methods=['POST'])
@admin_required
def add_harvest():
    connection = get_db_connection()
    
    if connection:
        try:
            plant_id = request.form.get('plant_id', None)
            if plant_id == '':
                plant_id = None
            harvest_date = request.form['harvest_date']
            quantity = request.form['quantity']
            unit = request.form.get('unit', 'kg')
            quality_grade = request.form.get('quality_grade', 'Grade A')
            notes = request.form.get('notes', '')
            
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO harvest 
                (plant_id, harvest_date, quantity, unit, quality_grade, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (plant_id, harvest_date, quantity, unit, quality_grade, notes))
            
            connection.commit()
            cursor.close()
            flash('Harvest record added successfully!', 'success')
        except Exception as e:
            print(f"Database error: {e}")
            flash('Error adding harvest record', 'error')
        finally:
            release_db_connection(connection)
    
    return redirect(url_for('harvesting'))

@app.route('/harvesting/delete/<int:id>', methods=['POST'])
@admin_required
def delete_harvest(id):
    connection = get_db_connection()
    
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM harvest WHERE id = %s", (id,))
            connection.commit()
            cursor.close()
            flash('Harvest record deleted successfully!', 'success')
        except Exception as e:
            print(f"Database error: {e}")
            flash('Error deleting record', 'error')
        finally:
            release_db_connection(connection)
    
    return redirect(url_for('harvesting'))

@app.route('/inventory')
@login_required
def inventory():
    connection = get_db_connection()
    items = []
    page = request.args.get('page', 1, type=int)
    per_page = 10
    total_items = 0
    
    if connection:
        try:
            cursor = connection.cursor(cursor_factory=extras.RealDictCursor)
            
            # Get total count
            cursor.execute("SELECT COUNT(*) as count FROM inventory")
            result = cursor.fetchone()
            total_items = result['count'] if result else 0
            
            # Get paginated items
            offset = (page - 1) * per_page
            cursor.execute("SELECT * FROM inventory ORDER BY item_name LIMIT %s OFFSET %s", (per_page, offset))
            items = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            release_db_connection(connection)
    
    total_pages = (total_items + per_page - 1) // per_page
    return render_template('inventory.html', inventory=items, page=page, total_pages=total_pages)

@app.route('/inventory/add', methods=['POST'])
@admin_required
def add_inventory():
    connection = get_db_connection()
    
    if connection:
        try:
            item_name = request.form['item_name']
            category = request.form['category']
            quantity = request.form['quantity']
            unit = request.form['unit']
            min_quantity = request.form.get('min_quantity', 0)
            supplier = request.form.get('supplier', '')
            
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO inventory 
                (item_name, category, quantity, unit, min_quantity, supplier)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (item_name, category, quantity, unit, min_quantity, supplier))
            
            connection.commit()
            cursor.close()
            flash('Inventory item added successfully!', 'success')
        except Exception as e:
            print(f"Database error: {e}")
            flash('Error adding inventory item', 'error')
        finally:
            release_db_connection(connection)
    
    return redirect(url_for('inventory'))

@app.route('/inventory/delete/<int:id>', methods=['POST'])
@admin_required
def delete_inventory(id):
    connection = get_db_connection()
    
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM inventory WHERE id = %s", (id,))
            connection.commit()
            cursor.close()
            flash('Inventory item deleted successfully!', 'success')
        except Exception as e:
            print(f"Database error: {e}")
            flash('Error deleting item', 'error')
        finally:
            release_db_connection(connection)
    
    return redirect(url_for('inventory'))

@app.route('/operations')
@login_required
def operations():
    connection = get_db_connection()
    ops = []
    
    if connection:
        try:
            cursor = connection.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute("SELECT * FROM operations ORDER BY operation_date DESC")
            ops = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            release_db_connection(connection)
    
    return render_template('operations.html', operations=ops)

@app.route('/operations/add', methods=['POST'])
@admin_required
def add_operation():
    connection = get_db_connection()
    
    if connection:
        try:
            operation_type = request.form['operation_type']
            operation_date = request.form['operation_date']
            field_location = request.form.get('field_location', '')
            description = request.form['description']
            cost = request.form.get('cost', 0)
            performed_by = request.form.get('performed_by', '')
            notes = request.form.get('notes', '')
            
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO operations 
                (operation_type, operation_date, field_location, description, cost, performed_by, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (operation_type, operation_date, field_location, description, cost, performed_by, notes))
            
            connection.commit()
            cursor.close()
            flash('Operation record added successfully!', 'success')
        except Exception as e:
            print(f"Database error: {e}")
            flash('Error adding operation record', 'error')
        finally:
            release_db_connection(connection)
    
    return redirect(url_for('operations'))

@app.route('/operations/delete/<int:id>', methods=['POST'])
@admin_required
def delete_operation(id):
    connection = get_db_connection()
    
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM operations WHERE id = %s", (id,))
            connection.commit()
            cursor.close()
            flash('Operation record deleted successfully!', 'success')
        except Exception as e:
            print(f"Database error: {e}")
            flash('Error deleting record', 'error')
        finally:
            release_db_connection(connection)
    
    return redirect(url_for('operations'))

@app.route('/sales')
@login_required
def sales():
    connection = get_db_connection()
    sale_records = []
    
    if connection:
        try:
            cursor = connection.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute("SELECT * FROM sales ORDER BY sale_date DESC")
            sale_records = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            release_db_connection(connection)
    
    return render_template('sales.html', sales=sale_records)

@app.route('/sales/add', methods=['POST'])
@admin_required
def add_sale():
    connection = get_db_connection()
    
    if connection:
        try:
            sale_date = request.form['sale_date']
            customer_name = request.form.get('customer_name', '')
            quantity = float(request.form['quantity'])
            unit = request.form.get('unit', 'kg')
            price_per_unit = float(request.form['price_per_unit'])
            total_amount = quantity * price_per_unit
            payment_status = request.form.get('payment_status', 'Pending')
            notes = request.form.get('notes', '')
            
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO sales 
                (sale_date, customer_name, quantity, unit, price_per_unit, total_amount, payment_status, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (sale_date, customer_name, quantity, unit, price_per_unit, total_amount, payment_status, notes))
            
            connection.commit()
            cursor.close()
            flash('Sale record added successfully!', 'success')
        except Exception as e:
            print(f"Database error: {e}")
            flash('Error adding sale record', 'error')
        finally:
            release_db_connection(connection)
    
    return redirect(url_for('sales'))

@app.route('/sales/delete/<int:id>', methods=['POST'])
@admin_required
def delete_sale(id):
    connection = get_db_connection()
    
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM sales WHERE id = %s", (id,))
            connection.commit()
            cursor.close()
            flash('Sale record deleted successfully!', 'success')
        except Exception as e:
            print(f"Database error: {e}")
            flash('Error deleting record', 'error')
        finally:
            release_db_connection(connection)
    
    return redirect(url_for('sales'))

@app.route('/employee_tasks')
@login_required
def employee_tasks():
    connection = get_db_connection()
    tasks = []
    
    if connection:
        try:
            cursor = connection.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute("""
                SELECT * FROM employee_tasks 
                ORDER BY task_date DESC, employee_number ASC
            """)
            tasks = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            release_db_connection(connection)
    
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('employee_tasks.html', tasks=tasks, today=today)

@app.route('/employee_tasks/add', methods=['POST'])
@admin_required
def add_employee_task():
    connection = get_db_connection()
    
    if connection:
        try:
            employee_number = int(request.form['employee_number'])
            task_date = request.form['task_date']
            task_type = request.form['task_type']
            field_location = request.form.get('field_location', '')
            description = request.form['description']
            start_time = request.form.get('start_time', None)
            if start_time == '':
                start_time = None
            estimated_hours = request.form.get('estimated_hours', None)
            if estimated_hours == '':
                estimated_hours = None
            status = request.form.get('status', 'Pending')
            
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO employee_tasks 
                (employee_number, task_date, task_type, field_location, description, 
                 start_time, estimated_hours, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (employee_number, task_date, task_type, field_location, description, 
                  start_time, estimated_hours, status))
            
            connection.commit()
            cursor.close()
            flash(f'Task assigned to Employee {employee_number} successfully!', 'success')
        except Exception as e:
            print(f"Database error: {e}")
            flash('Error assigning task', 'error')
        finally:
            release_db_connection(connection)
    
    return redirect(url_for('employee_tasks'))

@app.route('/employee_tasks/update_status/<int:id>', methods=['POST'])
@admin_required
def update_task_status(id):
    connection = get_db_connection()
    
    if connection:
        try:
            status = request.form['status']
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE employee_tasks 
                SET status = %s 
                WHERE id = %s
            """, (status, id))
            connection.commit()
            cursor.close()
            flash('Task status updated successfully!', 'success')
        except Exception as e:
            print(f"Database error: {e}")
            flash('Error updating task status', 'error')
        finally:
            release_db_connection(connection)
    
    return redirect(url_for('employee_tasks'))

@app.route('/employee_tasks/delete/<int:id>', methods=['POST'])
@admin_required
def delete_employee_task(id):
    connection = get_db_connection()
    
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM employee_tasks WHERE id = %s", (id,))
            connection.commit()
            cursor.close()
            flash('Task deleted successfully!', 'success')
        except Exception as e:
            print(f"Database error: {e}")
            flash('Error deleting task', 'error')
        finally:
            release_db_connection(connection)
    
    return redirect(url_for('employee_tasks'))

if __name__ == '__main__':
    print("Initializing connection pool...")
    init_pool()
    print("Initializing database...")
    init_db()
    print("Starting Flask server on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
