from flask import Flask, render_template, request, redirect, url_for, flash
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'tomato-farm-secret-key-2025')
CORS(app)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'farmdb'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_db():
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = connection.cursor()
        
        with open('database/schema.sql', 'r') as f:
            sql_script = f.read()
        
        for statement in sql_script.split(';'):
            if statement.strip():
                cursor.execute(statement)
        
        connection.commit()
        cursor.close()
        connection.close()
        print("Database initialized successfully!")
    except Error as e:
        print(f"Error initializing database: {e}")

@app.route('/')
def index():
    connection = get_db_connection()
    stats = {
        'total_plants': 0,
        'total_harvest': 0,
        'inventory_items': 0,
        'total_sales': 0
    }
    recent_activities = []
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
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
                       CONCAT(variety, ' - ', quantity, ' plants') as details
                FROM tomato_plants 
                ORDER BY planting_date DESC LIMIT 5
            """)
            recent_activities = cursor.fetchall()
            
            cursor.close()
        except Error as e:
            print(f"Database error: {e}")
        finally:
            connection.close()
    
    return render_template('index.html', stats=stats, recent_activities=recent_activities)

@app.route('/planting')
def planting():
    connection = get_db_connection()
    plants = []
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM tomato_plants 
                ORDER BY planting_date DESC
            """)
            plants = cursor.fetchall()
            cursor.close()
        except Error as e:
            print(f"Database error: {e}")
        finally:
            connection.close()
    
    return render_template('planting.html', plants=plants)

@app.route('/planting/add', methods=['POST'])
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
        except Error as e:
            print(f"Database error: {e}")
            flash('Error adding planting record', 'error')
        finally:
            connection.close()
    
    return redirect(url_for('planting'))

@app.route('/planting/delete/<int:id>', methods=['POST'])
def delete_planting(id):
    connection = get_db_connection()
    
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM tomato_plants WHERE id = %s", (id,))
            connection.commit()
            cursor.close()
            flash('Planting record deleted successfully!', 'success')
        except Error as e:
            print(f"Database error: {e}")
            flash('Error deleting record', 'error')
        finally:
            connection.close()
    
    return redirect(url_for('planting'))

@app.route('/harvesting')
def harvesting():
    connection = get_db_connection()
    harvests = []
    plants = []
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT h.*, p.variety as plant_variety
                FROM harvest h
                LEFT JOIN tomato_plants p ON h.plant_id = p.id
                ORDER BY h.harvest_date DESC
            """)
            harvests = cursor.fetchall()
            
            cursor.execute("SELECT * FROM tomato_plants ORDER BY planting_date DESC")
            plants = cursor.fetchall()
            
            cursor.close()
        except Error as e:
            print(f"Database error: {e}")
        finally:
            connection.close()
    
    return render_template('harvesting.html', harvests=harvests, plants=plants)

@app.route('/harvesting/add', methods=['POST'])
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
        except Error as e:
            print(f"Database error: {e}")
            flash('Error adding harvest record', 'error')
        finally:
            connection.close()
    
    return redirect(url_for('harvesting'))

@app.route('/harvesting/delete/<int:id>', methods=['POST'])
def delete_harvest(id):
    connection = get_db_connection()
    
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM harvest WHERE id = %s", (id,))
            connection.commit()
            cursor.close()
            flash('Harvest record deleted successfully!', 'success')
        except Error as e:
            print(f"Database error: {e}")
            flash('Error deleting record', 'error')
        finally:
            connection.close()
    
    return redirect(url_for('harvesting'))

@app.route('/inventory')
def inventory():
    connection = get_db_connection()
    items = []
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM inventory ORDER BY item_name")
            items = cursor.fetchall()
            cursor.close()
        except Error as e:
            print(f"Database error: {e}")
        finally:
            connection.close()
    
    return render_template('inventory.html', inventory=items)

@app.route('/inventory/add', methods=['POST'])
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
        except Error as e:
            print(f"Database error: {e}")
            flash('Error adding inventory item', 'error')
        finally:
            connection.close()
    
    return redirect(url_for('inventory'))

@app.route('/inventory/delete/<int:id>', methods=['POST'])
def delete_inventory(id):
    connection = get_db_connection()
    
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM inventory WHERE id = %s", (id,))
            connection.commit()
            cursor.close()
            flash('Inventory item deleted successfully!', 'success')
        except Error as e:
            print(f"Database error: {e}")
            flash('Error deleting item', 'error')
        finally:
            connection.close()
    
    return redirect(url_for('inventory'))

@app.route('/operations')
def operations():
    connection = get_db_connection()
    ops = []
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM operations ORDER BY operation_date DESC")
            ops = cursor.fetchall()
            cursor.close()
        except Error as e:
            print(f"Database error: {e}")
        finally:
            connection.close()
    
    return render_template('operations.html', operations=ops)

@app.route('/operations/add', methods=['POST'])
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
        except Error as e:
            print(f"Database error: {e}")
            flash('Error adding operation record', 'error')
        finally:
            connection.close()
    
    return redirect(url_for('operations'))

@app.route('/operations/delete/<int:id>', methods=['POST'])
def delete_operation(id):
    connection = get_db_connection()
    
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM operations WHERE id = %s", (id,))
            connection.commit()
            cursor.close()
            flash('Operation record deleted successfully!', 'success')
        except Error as e:
            print(f"Database error: {e}")
            flash('Error deleting record', 'error')
        finally:
            connection.close()
    
    return redirect(url_for('operations'))

@app.route('/sales')
def sales():
    connection = get_db_connection()
    sale_records = []
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM sales ORDER BY sale_date DESC")
            sale_records = cursor.fetchall()
            cursor.close()
        except Error as e:
            print(f"Database error: {e}")
        finally:
            connection.close()
    
    return render_template('sales.html', sales=sale_records)

@app.route('/sales/add', methods=['POST'])
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
        except Error as e:
            print(f"Database error: {e}")
            flash('Error adding sale record', 'error')
        finally:
            connection.close()
    
    return redirect(url_for('sales'))

@app.route('/sales/delete/<int:id>', methods=['POST'])
def delete_sale(id):
    connection = get_db_connection()
    
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM sales WHERE id = %s", (id,))
            connection.commit()
            cursor.close()
            flash('Sale record deleted successfully!', 'success')
        except Error as e:
            print(f"Database error: {e}")
            flash('Error deleting record', 'error')
        finally:
            connection.close()
    
    return redirect(url_for('sales'))

if __name__ == '__main__':
    print("Initializing database...")
    init_db()
    print("Starting Flask server on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
