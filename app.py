import mysql.connector
from mysql.connector import Error
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid
import os
from PIL import Image
import io

# Database connection function
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1713$",
            database="farm_v5"
        )
        return connection
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None

# Initialize database schema
def init_database():
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE DATABASE IF NOT EXISTS farm;
            """)
            cursor.execute("USE farm;")
            
            # Create tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Animal_Category (
                    category_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) UNIQUE,
                    description TEXT,
                    image LONGBLOB
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Animal (
                    animal_id INT AUTO_INCREMENT PRIMARY KEY,
                    tag_number VARCHAR(50) UNIQUE,
                    category_id INT,
                    breed VARCHAR(100),
                    arrival_date DATE,
                    initial_weight_kg FLOAT,
                    image LONGBLOB,
                    FOREIGN KEY (category_id) REFERENCES Animal_Category(category_id)
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Staff (
                    staff_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100),
                    role VARCHAR(100),
                    salary_per_month FLOAT,
                    image LONGBLOB
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Expense_Summary (
                    expense_id INT AUTO_INCREMENT PRIMARY KEY,
                    month DATE,
                    total_feed_cost FLOAT,
                    total_medicine_cost FLOAT,
                    total_salaries FLOAT,
                    total_utilities FLOAT,
                    other_expenses FLOAT,
                    total_expense FLOAT
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Monthly_Weight (
                    weight_id INT AUTO_INCREMENT PRIMARY KEY,
                    animal_id INT,
                    month DATE,
                    weight_kg FLOAT,
                    FOREIGN KEY (animal_id) REFERENCES Animal(animal_id)
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Feed_Record (
                    feed_id INT AUTO_INCREMENT PRIMARY KEY,
                    animal_id INT,
                    date DATE,
                    feed_type VARCHAR(100),
                    quantity_kg FLOAT,
                    cost FLOAT,
                    FOREIGN KEY (animal_id) REFERENCES Animal(animal_id)
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Medicine_Record (
                    medicine_id INT AUTO_INCREMENT PRIMARY KEY,
                    animal_id INT,
                    date DATE,
                    medicine_name VARCHAR(100),
                    quantity VARCHAR(50),
                    cost FLOAT,
                    remarks TEXT,
                    FOREIGN KEY (animal_id) REFERENCES Animal(animal_id)
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Utility_Bill (
                    bill_id INT AUTO_INCREMENT PRIMARY KEY,
                    month DATE,
                    type VARCHAR(50),
                    amount FLOAT
                );
            """)
            connection.commit()
        except Error as e:
            st.error(f"Error initializing database: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

# Page configuration
st.set_page_config(
    page_title="Farm Management System",
    page_icon="🐄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .sidebar .sidebar-content {
        background-color: #e9ecef;
    }
    h1, h2, h3, h4 {
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    .stButton>button {
        background-color: #28a745;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
    }
    .stDataFrame {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .animal-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    .animal-card:hover {
        transform: translateY(-5px);
    }
    .category-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    .category-card:hover {
        transform: translateY(-5px);
    }
    .image-preview {
        max-width: 200px;
        max-height: 200px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .form-container {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .action-buttons {
        display: flex;
        gap: 10px;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Helper function to display images from binary data
def display_image(binary_data):
    if binary_data:
        image = Image.open(io.BytesIO(binary_data))
        st.image(image, use_column_width=True)
    else:
        st.warning("No image available")

# Sidebar navigation
st.sidebar.title("🐄 Farm Management")
page = st.sidebar.radio("Navigation", [
    "Dashboard",
    "Animal Categories",
    "Animal Records",
    "Weight Tracking",
    "Feed Records",
    "Medical Records",
    "Staff Management",
    "Financial Overview"
])

# Initialize database
init_database()

# Dashboard Page
if page == "Dashboard":
    st.title("Farm Dashboard")
    
    connection = create_connection()
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Get animal count
            cursor.execute("SELECT COUNT(*) as count FROM Animal")
            animal_count = cursor.fetchone()['count'] if cursor.rowcount > 0 else 0
            
            # Get staff count
            cursor.execute("SELECT COUNT(*) as count FROM Staff")
            staff_count = cursor.fetchone()['count'] if cursor.rowcount > 0 else 0
            
            # Get total expenses
            cursor.execute("SELECT SUM(total_expense) as total FROM Expense_Summary")
            total_expenses = cursor.fetchone()['total'] if cursor.rowcount > 0 and cursor.fetchone()['total'] else 0.0
            
            # Get average weight gain
            cursor.execute("""
                SELECT AVG(mw.weight_kg - a.initial_weight_kg) as avg_gain 
                FROM Monthly_Weight mw
                JOIN Animal a ON mw.animal_id = a.animal_id
                WHERE mw.month = (SELECT MAX(month) FROM Monthly_Weight)
            """)
            avg_gain = cursor.fetchone()['avg_gain'] if cursor.rowcount > 0 and cursor.fetchone()['avg_gain'] else 0.0
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Animals</h3>
                    <h1>{animal_count}</h1>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Staff</h3>
                    <h1>{staff_count}</h1>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Monthly Expenses</h3>
                    <h1>${total_expenses:,.2f}</h1>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Avg Weight Gain</h3>
                    <h1>{avg_gain:.2f} kg</h1>
                </div>
                """, unsafe_allow_html=True)
            
            # Weight gain chart
            st.subheader("Animal Weight Progress")
            cursor.execute("""
                SELECT a.tag_number, a.breed, a.initial_weight_kg, mw.weight_kg, 
                       mw.weight_kg - a.initial_weight_kg as weight_gain
                FROM Animal a
                JOIN Monthly_Weight mw ON a.animal_id = mw.animal_id
                WHERE mw.month = (SELECT MAX(month) FROM Monthly_Weight)
            """)
            weight_data = pd.DataFrame(cursor.fetchall())
            
            if not weight_data.empty:
                fig = px.bar(weight_data, x='tag_number', y='weight_gain',
                             color='breed', text='weight_gain',
                             title="Weight Gain by Animal")
                fig.update_traces(texttemplate='%{text:.2f}kg', textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
            
            # Expense breakdown
            st.subheader("Monthly Expense Breakdown")
            cursor.execute("""
                SELECT month, total_feed_cost, total_medicine_cost, 
                       total_salaries, total_utilities, other_expenses
                FROM Expense_Summary
                ORDER BY month DESC
                LIMIT 5
            """)
            expense_data = pd.DataFrame(cursor.fetchall())
            
            if not expense_data.empty:
                # Convert month to string if not datetime
                if not pd.api.types.is_datetime64_any_dtype(expense_data['month']):
                    expense_data['month'] = pd.to_datetime(expense_data['month']).dt.strftime('%Y-%m')
                else:
                    expense_data['month'] = expense_data['month'].dt.strftime('%Y-%m')
                fig = px.bar(expense_data, x='month',
                            y=['total_feed_cost', 'total_medicine_cost',
                               'total_salaries', 'total_utilities', 'other_expenses'],
                            title="Expense Breakdown by Category",
                            labels={'value': 'Amount ($)', 'variable': 'Category'})
                st.plotly_chart(fig, use_container_width=True)
            
            # Recent Animals
            st.subheader("Recent Animals")
            cursor.execute("""
                SELECT a.*, ac.name as category_name 
                FROM Animal a
                LEFT JOIN Animal_Category ac ON a.category_id = ac.category_id
                ORDER BY a.arrival_date DESC
                LIMIT 4
            """)
            recent_animals = cursor.fetchall()
            
            if recent_animals:
                cols = st.columns(4)
                for idx, animal in enumerate(recent_animals):
                    with cols[idx % 4]:
                        st.markdown(f"""
                            <div class="animal-card">
                                <h4>{animal['tag_number']}</h4>
                                <p><strong>Breed:</strong> {animal['breed']}</p>
                                <p><strong>Category:</strong> {animal['category_name'] or 'N/A'}</p>
                                <p><strong>Arrival:</strong> {animal['arrival_date']}</p>
                        """, unsafe_allow_html=True)
                        if animal['image']:
                            display_image(animal['image'])
                        st.markdown("</div>", unsafe_allow_html=True)
            
        except Error as e:
            st.error(f"Error retrieving data: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

# Animal Categories Page
elif page == "Animal Categories":
    st.title("Animal Categories Management")
    connection = create_connection()
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Display all categories
            st.subheader("All Animal Categories")
            
            cursor.execute("SELECT * FROM Animal_Category")
            categories = cursor.fetchall()
            
            if categories:
                cols = st.columns(3)
                for idx, category in enumerate(categories):
                    with cols[idx % 3]:
                        st.markdown(f"""
                            <div class="category-card">
                                <h3>{category['name']}</h3>
                                <p>{category['description'] or 'No description'}</p>
                        """, unsafe_allow_html=True)
                        if category['image']:
                            display_image(category['image'])
                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("No animal categories found.")
            
            # Action buttons below the heading
            st.subheader("Actions")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("➕ Add New Category"):
                    st.session_state.show_add_category = True
            
            with col2:
                if categories:
                    if st.button("✏️ Update Category"):
                        st.session_state.show_update_category = True
            
            with col3:
                if categories:
                    if st.button("🗑️ Delete Category"):
                        st.session_state.show_delete_category = True
            
            # Add new category form
            if st.session_state.get('show_add_category', False):
                with st.form("category_form"):
                    st.subheader("Add New Category")
                    name = st.text_input("Category Name*")
                    description = st.text_area("Description")
                    image = st.file_uploader("Category Image", type=['jpg', 'jpeg', 'png'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Add Category"):
                            if name:
                                try:
                                    image_data = image.read() if image else None
                                    cursor.execute("""
                                        INSERT INTO Animal_Category (name, description, image)
                                        VALUES (%s, %s, %s)
                                    """, (name, description, image_data))
                                    connection.commit()
                                    st.success("Category added successfully!")
                                    st.session_state.show_add_category = False
                                    st.rerun()
                                except Error as e:
                                    st.error(f"Error adding category: {e}")
                            else:
                                st.error("Category name is required")
                    with col2:
                        if st.form_submit_button("Cancel"):
                            st.session_state.show_add_category = False
            
            # Update category form
            if st.session_state.get('show_update_category', False) and categories:
                with st.form("update_category_form"):
                    st.subheader("Update Category")
                    
                    category_options = {f"{c['name']} (ID: {c['category_id']})": c['category_id'] for c in categories}
                    selected_category = st.selectbox("Select Category", options=list(category_options.keys()))
                    
                    if selected_category:
                        category_id = category_options[selected_category]
                        cursor.execute("SELECT * FROM Animal_Category WHERE category_id = %s", (category_id,))
                        category_data = cursor.fetchone()
                        
                        new_name = st.text_input("Name", value=category_data['name'])
                        new_description = st.text_area("Description", value=category_data['description'] or "")
                        new_image = st.file_uploader("Update Image", type=['jpg', 'jpeg', 'png'])
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Update Category"):
                                try:
                                    image_data = new_image.read() if new_image else category_data['image']
                                    cursor.execute("""
                                        UPDATE Animal_Category 
                                        SET name = %s, description = %s, image = %s
                                        WHERE category_id = %s
                                    """, (new_name, new_description, image_data, category_id))
                                    connection.commit()
                                    st.success("Category updated successfully!")
                                    st.session_state.show_update_category = False
                                    st.rerun()
                                except Error as e:
                                    st.error(f"Error updating category: {e}")
                        with col2:
                            if st.form_submit_button("Cancel"):
                                st.session_state.show_update_category = False
            
            # Delete category form
            if st.session_state.get('show_delete_category', False) and categories:
                with st.form("delete_category_form"):
                    st.subheader("Delete Category")
                    st.warning("Warning: This action cannot be undone")
                    
                    category_options = {f"{c['name']} (ID: {c['category_id']})": c['category_id'] for c in categories}
                    selected_category = st.selectbox("Select Category to Delete", options=list(category_options.keys()))
                    
                    if selected_category:
                        category_id = category_options[selected_category]
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Delete Category"):
                                try:
                                    # Check if any animals are using this category
                                    cursor.execute("SELECT COUNT(*) as count FROM Animal WHERE category_id = %s", (category_id,))
                                    animal_count = cursor.fetchone()['count']
                                    
                                    if animal_count > 0:
                                        st.error(f"Cannot delete category - {animal_count} animals are associated with it")
                                    else:
                                        cursor.execute("DELETE FROM Animal_Category WHERE category_id = %s", (category_id,))
                                        connection.commit()
                                        st.success("Category deleted successfully!")
                                        st.session_state.show_delete_category = False
                                        st.rerun()
                                except Error as e:
                                    st.error(f"Error deleting category: {e}")
                        with col2:
                            if st.form_submit_button("Cancel"):
                                st.session_state.show_delete_category = False
            
        except Error as e:
            st.error(f"Error retrieving data: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

# Animal Records Page
elif page == "Animal Records":
    st.title("Animal Records Management")
    connection = create_connection()
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Get categories for dropdown
            cursor.execute("SELECT category_id, name FROM Animal_Category")
            categories = cursor.fetchall()
            category_options = {c['name']: c['category_id'] for c in categories}
            category_options["Uncategorized"] = None
            
            # Display all animals
            st.subheader("All Animals")
            
            cursor.execute("""
                SELECT a.*, ac.name as category_name 
                FROM Animal a
                LEFT JOIN Animal_Category ac ON a.category_id = ac.category_id
            """)
            animals = cursor.fetchall()
            
            search_term = st.text_input("Search Animals by Tag Number or Breed")
            
            if search_term:
                filtered_animals = [a for a in animals if 
                                  search_term.lower() in a['tag_number'].lower() or 
                                  (a['breed'] and search_term.lower() in a['breed'].lower())]
            else:
                filtered_animals = animals
            
            if filtered_animals:
                cols = st.columns(3)
                for idx, animal in enumerate(filtered_animals):
                    with cols[idx % 3]:
                        st.markdown(f"""
                            <div class="animal-card">
                                <h3>{animal['tag_number']}</h3>
                                <p><strong>Breed:</strong> {animal['breed']}</p>
                                <p><strong>Category:</strong> {animal['category_name'] or 'Uncategorized'}</p>
                                <p><strong>Arrival:</strong> {animal['arrival_date']}</p>
                                <p><strong>Initial Weight:</strong> {animal['initial_weight_kg']} kg</p>
                        """, unsafe_allow_html=True)
                        if animal['image']:
                            display_image(animal['image'])
                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("No animals found matching your search criteria.")
            
            # Action buttons below the heading
            st.subheader("Actions")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("➕ Add New Animal"):
                    st.session_state.show_add_animal = True
            
            with col2:
                if animals:
                    if st.button("✏️ Update Animal"):
                        st.session_state.show_update_animal = True
            
            with col3:
                if animals:
                    if st.button("🗑️ Delete Animal"):
                        st.session_state.show_delete_animal = True
            
            # Add new animal form
            if st.session_state.get('show_add_animal', False):
                with st.form("animal_form"):
                    st.subheader("Add New Animal")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        tag_number = st.text_input("Tag Number*")
                        breed = st.text_input("Breed")
                        category = st.selectbox("Category", options=list(category_options.keys()))
                        arrival_date = st.date_input("Arrival Date")
                    
                    with col2:
                        initial_weight = st.number_input("Initial Weight (kg)*", min_value=0.0, step=0.1)
                        image = st.file_uploader("Animal Image", type=['jpg', 'jpeg', 'png'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Add Animal"):
                            if tag_number and initial_weight:
                                try:
                                    image_data = image.read() if image else None
                                    category_id = category_options[category]
                                    cursor.execute("""
                                        INSERT INTO Animal (tag_number, category_id, breed, arrival_date, initial_weight_kg, image)
                                        VALUES (%s, %s, %s, %s, %s, %s)
                                    """, (tag_number, category_id, breed, arrival_date, initial_weight, image_data))
                                    connection.commit()
                                    st.success("Animal added successfully!")
                                    st.session_state.show_add_animal = False
                                    st.rerun()
                                except Error as e:
                                    st.error(f"Error adding animal: {e}")
                            else:
                                st.error("Tag number and initial weight are required")
                    with col2:
                        if st.form_submit_button("Cancel"):
                            st.session_state.show_add_animal = False
            
            # Update animal form
            if st.session_state.get('show_update_animal', False) and animals:
                with st.form("edit_animal_form"):
                    st.subheader("Update Animal")
                    
                    animal_options = {f"{a['tag_number']} (ID: {a['animal_id']})": a['animal_id'] for a in animals}
                    selected_animal = st.selectbox("Select Animal", options=list(animal_options.keys()))
                    
                    if selected_animal:
                        animal_id = animal_options[selected_animal]
                        cursor.execute("""
                            SELECT a.*, ac.name as category_name 
                            FROM Animal a
                            LEFT JOIN Animal_Category ac ON a.category_id = ac.category_id
                            WHERE a.animal_id = %s
                        """, (animal_id,))
                        animal_data = cursor.fetchone()
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            new_tag = st.text_input("Tag Number", value=animal_data['tag_number'])
                            new_breed = st.text_input("Breed", value=animal_data['breed'] or "")
                            
                            # Get current category name
                            current_category = animal_data['category_name'] or "Uncategorized"
                            new_category = st.selectbox(
                                "Category", 
                                options=list(category_options.keys()),
                                index=list(category_options.keys()).index(current_category)
                            )
                            
                            new_arrival = st.date_input("Arrival Date", value=animal_data['arrival_date'])
                        
                        with col2:
                            new_weight = st.number_input(
                                "Initial Weight (kg)", 
                                min_value=0.0, 
                                step=0.1,
                                value=animal_data['initial_weight_kg']
                            )
                            new_image = st.file_uploader("Update Image", type=['jpg', 'jpeg', 'png'])
                            
                            if animal_data['image']:
                                st.markdown("**Current Image:**")
                                display_image(animal_data['image'])
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Update Animal"):
                                try:
                                    image_data = new_image.read() if new_image else animal_data['image']
                                    category_id = category_options[new_category]
                                    cursor.execute("""
                                        UPDATE Animal 
                                        SET tag_number = %s, category_id = %s, breed = %s, 
                                            arrival_date = %s, initial_weight_kg = %s, image = %s
                                        WHERE animal_id = %s
                                    """, (new_tag, category_id, new_breed, new_arrival, new_weight, image_data, animal_id))
                                    connection.commit()
                                    st.success("Animal updated successfully!")
                                    st.session_state.show_update_animal = False
                                    st.rerun()
                                except Error as e:
                                    st.error(f"Error updating animal: {e}")
                        with col2:
                            if st.form_submit_button("Cancel"):
                                st.session_state.show_update_animal = False
            
            # Delete animal form
            if st.session_state.get('show_delete_animal', False) and animals:
                with st.form("delete_animal_form"):
                    st.subheader("Delete Animal")
                    st.warning("Warning: This action cannot be undone")
                    
                    animal_options = {f"{a['tag_number']} (ID: {a['animal_id']})": a['animal_id'] for a in animals}
                    selected_animal = st.selectbox("Select Animal to Delete", options=list(animal_options.keys()))
                    
                    if selected_animal:
                        animal_id = animal_options[selected_animal]
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Delete Animal"):
                                try:
                                    # Check for dependent records
                                    cursor.execute("SELECT COUNT(*) as count FROM Monthly_Weight WHERE animal_id = %s", (animal_id,))
                                    weight_records = cursor.fetchone()['count']
                                    
                                    cursor.execute("SELECT COUNT(*) as count FROM Feed_Record WHERE animal_id = %s", (animal_id,))
                                    feed_records = cursor.fetchone()['count']
                                    
                                    cursor.execute("SELECT COUNT(*) as count FROM Medicine_Record WHERE animal_id = %s", (animal_id,))
                                    med_records = cursor.fetchone()['count']
                                    
                                    if weight_records > 0 or feed_records > 0 or med_records > 0:
                                        st.error(f"Cannot delete animal - it has {weight_records} weight records, {feed_records} feed records, and {med_records} medical records")
                                    else:
                                        cursor.execute("DELETE FROM Animal WHERE animal_id = %s", (animal_id,))
                                        connection.commit()
                                        st.success("Animal deleted successfully!")
                                        st.session_state.show_delete_animal = False
                                        st.rerun()
                                except Error as e:
                                    st.error(f"Error deleting animal: {e}")
                        with col2:
                            if st.form_submit_button("Cancel"):
                                st.session_state.show_delete_animal = False
            
        except Error as e:
            st.error(f"Error retrieving data: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

# Weight Tracking Page
elif page == "Weight Tracking":
    st.title("Animal Weight Tracking")
    connection = create_connection()
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Get animals for dropdown
            cursor.execute("SELECT animal_id, tag_number FROM Animal")
            animals = cursor.fetchall()
            animal_options = {f"{a['tag_number']} (ID: {a['animal_id']})": a['animal_id'] for a in animals}
            
            # View weight records
            st.subheader("Weight Records")
            selected_animal_view = st.selectbox("Select Animal to View", options=["All"] + list(animal_options.keys()))
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            
            if selected_animal_view != "All":
                animal_id = animal_options[selected_animal_view]
                cursor.execute("""
                    SELECT mw.month, mw.weight_kg, a.tag_number, a.breed
                    FROM Monthly_Weight mw
                    JOIN Animal a ON mw.animal_id = a.animal_id
                    WHERE mw.animal_id = %s AND mw.month BETWEEN %s AND %s
                    ORDER BY mw.month DESC
                """, (animal_id, start_date, end_date))
            else:
                cursor.execute("""
                    SELECT mw.month, mw.weight_kg, a.tag_number, a.breed
                    FROM Monthly_Weight mw
                    JOIN Animal a ON mw.animal_id = a.animal_id
                    WHERE mw.month BETWEEN %s AND %s
                    ORDER BY mw.month DESC
                """, (start_date, end_date))
            
            weight_records = pd.DataFrame(cursor.fetchall())
            
            if not weight_records.empty:
                st.dataframe(weight_records, use_container_width=True)
                
                # Plot weight progress
                if selected_animal_view != "All":
                    fig = px.line(weight_records, x='month', y='weight_kg',
                                 title=f"Weight Progress for {selected_animal_view}",
                                 markers=True)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No weight records found for the selected period.")
            
            # Action buttons below the heading
            st.subheader("Actions")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("➕ Add Weight Record"):
                    st.session_state.show_add_weight = True
            
            with col2:
                if not weight_records.empty:
                    if st.button("✏️ Update Weight Record"):
                        st.session_state.show_update_weight = True
            
            # Add new weight record form
            if st.session_state.get('show_add_weight', False):
                with st.form("weight_form"):
                    st.subheader("Add New Weight Record")
                    selected_animal = st.selectbox("Select Animal", options=list(animal_options.keys()))
                    month = st.date_input("Month")
                    weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Add Weight Record"):
                            animal_id = animal_options[selected_animal]
                            try:
                                cursor.execute("""
                                    INSERT INTO Monthly_Weight (animal_id, month, weight_kg)
                                    VALUES (%s, %s, %s)
                                """, (animal_id, month, weight))
                                connection.commit()
                                st.success("Weight record added successfully!")
                                st.session_state.show_add_weight = False
                                st.rerun()
                            except Error as e:
                                st.error(f"Error adding weight record: {e}")
                    with col2:
                        if st.form_submit_button("Cancel"):
                            st.session_state.show_add_weight = False
            
            # Update weight record form
            if st.session_state.get('show_update_weight', False) and not weight_records.empty:
                with st.form("update_weight_form"):
                    st.subheader("Update Weight Record")
                    
                    selected_record = st.selectbox("Select Record to Update", 
                                                 options=weight_records['month'].astype(str) + " - " + weight_records['tag_number'])
                    
                    if selected_record:
                        record_date = pd.to_datetime(selected_record.split(" - ")[0]).date()
                        tag_number = selected_record.split(" - ")[1]
                        
                        cursor.execute("""
                            SELECT mw.weight_id, mw.weight_kg 
                            FROM Monthly_Weight mw
                            JOIN Animal a ON mw.animal_id = a.animal_id
                            WHERE mw.month = %s AND a.tag_number = %s
                        """, (record_date, tag_number))
                        record_data = cursor.fetchone()
                        
                        if record_data:
                            new_weight = st.number_input("New Weight (kg)", 
                                                       min_value=0.0, 
                                                       step=0.1,
                                                       value=record_data['weight_kg'])
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("Update Weight"):
                                    try:
                                        cursor.execute("""
                                            UPDATE Monthly_Weight 
                                            SET weight_kg = %s
                                            WHERE weight_id = %s
                                        """, (new_weight, record_data['weight_id']))
                                        connection.commit()
                                        st.success("Weight record updated successfully!")
                                        st.session_state.show_update_weight = False
                                        st.rerun()
                                    except Error as e:
                                        st.error(f"Error updating weight record: {e}")
                            with col2:
                                if st.form_submit_button("Cancel"):
                                    st.session_state.show_update_weight = False
            
        except Error as e:
            st.error(f"Error retrieving data: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

# Feed Records Page
elif page == "Feed Records":
    st.title("Feed Records Management")
    connection = create_connection()
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Get animals for dropdown
            cursor.execute("SELECT animal_id, tag_number FROM Animal")
            animals = cursor.fetchall()
            animal_options = {f"{a['tag_number']} (ID: {a['animal_id']})": a['animal_id'] for a in animals}
            
            # View feed records
            st.subheader("Feed Records")
            selected_animal_view = st.selectbox("Select Animal to View", options=["All"] + list(animal_options.keys()))
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            
            if selected_animal_view != "All":
                animal_id = animal_options[selected_animal_view]
                cursor.execute("""
                    SELECT fr.date, fr.feed_type, fr.quantity_kg, fr.cost, a.tag_number
                    FROM Feed_Record fr
                    JOIN Animal a ON fr.animal_id = a.animal_id
                    WHERE fr.animal_id = %s AND fr.date BETWEEN %s AND %s
                    ORDER BY fr.date DESC
                """, (animal_id, start_date, end_date))
            else:
                cursor.execute("""
                    SELECT fr.date, fr.feed_type, fr.quantity_kg, fr.cost, a.tag_number
                    FROM Feed_Record fr
                    JOIN Animal a ON fr.animal_id = a.animal_id
                    WHERE fr.date BETWEEN %s AND %s
                    ORDER BY fr.date DESC
                """, (start_date, end_date))
            
            feed_records = pd.DataFrame(cursor.fetchall())
            
            if not feed_records.empty:
                st.dataframe(feed_records, use_container_width=True)
                
                # Calculate total feed cost
                total_cost = feed_records['cost'].sum()
                st.metric("Total Feed Cost", f"${total_cost:,.2f}")
                
                # Plot feed types
                if selected_animal_view != "All":
                    fig = px.pie(feed_records, names='feed_type', values='quantity_kg',
                                title=f"Feed Type Distribution for {selected_animal_view}")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No feed records found for the selected period.")
            
            # Action buttons below the heading
            st.subheader("Actions")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("➕ Add Feed Record"):
                    st.session_state.show_add_feed = True
            
            with col2:
                if not feed_records.empty:
                    if st.button("✏️ Update Feed Record"):
                        st.session_state.show_update_feed = True
            
            # Add new feed record form
            if st.session_state.get('show_add_feed', False):
                with st.form("feed_form"):
                    st.subheader("Add New Feed Record")
                    selected_animal = st.selectbox("Select Animal", options=list(animal_options.keys()))
                    date = st.date_input("Date")
                    feed_type = st.text_input("Feed Type*")
                    quantity = st.number_input("Quantity (kg)*", min_value=0.0, step=0.1)
                    cost = st.number_input("Cost ($)*", min_value=0.0, step=0.01)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Add Feed Record"):
                            if feed_type and quantity and cost:
                                animal_id = animal_options[selected_animal]
                                try:
                                    cursor.execute("""
                                        INSERT INTO Feed_Record (animal_id, date, feed_type, quantity_kg, cost)
                                        VALUES (%s, %s, %s, %s, %s)
                                    """, (animal_id, date, feed_type, quantity, cost))
                                    connection.commit()
                                    st.success("Feed record added successfully!")
                                    st.session_state.show_add_feed = False
                                    st.rerun()
                                except Error as e:
                                    st.error(f"Error adding feed record: {e}")
                            else:
                                st.error("Feed type, quantity, and cost are required")
                    with col2:
                        if st.form_submit_button("Cancel"):
                            st.session_state.show_add_feed = False
            
            # Update feed record form
            if st.session_state.get('show_update_feed', False) and not feed_records.empty:
                with st.form("update_feed_form"):
                    st.subheader("Update Feed Record")
                    
                    selected_record = st.selectbox("Select Record to Update", 
                                                options=feed_records['date'].astype(str) + " - " + 
                                                feed_records['tag_number'] + " - " + 
                                                feed_records['feed_type'])
                    
                    if selected_record:
                        parts = selected_record.split(" - ")
                        record_date = pd.to_datetime(parts[0]).date()
                        tag_number = parts[1]
                        feed_type = parts[2]
                        
                        cursor.execute("""
                            SELECT fr.feed_id, fr.quantity_kg, fr.cost
                            FROM Feed_Record fr
                            JOIN Animal a ON fr.animal_id = a.animal_id
                            WHERE fr.date = %s AND a.tag_number = %s AND fr.feed_type = %s
                        """, (record_date, tag_number, feed_type))
                        record_data = cursor.fetchone()
                        
                        if record_data:
                            new_quantity = st.number_input("New Quantity (kg)", 
                                                        min_value=0.0, 
                                                        step=0.1,
                                                        value=record_data['quantity_kg'])
                            new_cost = st.number_input("New Cost ($)", 
                                                    min_value=0.0, 
                                                    step=0.01,
                                                    value=record_data['cost'])
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("Update Feed Record"):
                                    try:
                                        cursor.execute("""
                                            UPDATE Feed_Record 
                                            SET quantity_kg = %s, cost = %s
                                            WHERE feed_id = %s
                                        """, (new_quantity, new_cost, record_data['feed_id']))
                                        connection.commit()
                                        st.success("Feed record updated successfully!")
                                        st.session_state.show_update_feed = False
                                        st.rerun()
                                    except Error as e:
                                        st.error(f"Error updating feed record: {e}")
                            with col2:
                                if st.form_submit_button("Cancel"):
                                    st.session_state.show_update_feed = False
            
        except Error as e:
            st.error(f"Error retrieving data: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

# Medical Records Page
elif page == "Medical Records":
    st.title("Medical Records Management")
    connection = create_connection()
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Get animals for dropdown
            cursor.execute("SELECT animal_id, tag_number FROM Animal")
            animals = cursor.fetchall()
            animal_options = {f"{a['tag_number']} (ID: {a['animal_id']})": a['animal_id'] for a in animals}
            
            # View medical records
            st.subheader("Medical Records")
            selected_animal_view = st.selectbox("Select Animal to View", options=["All"] + list(animal_options.keys()))
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            
            if selected_animal_view != "All":
                animal_id = animal_options[selected_animal_view]
                cursor.execute("""
                    SELECT mr.date, mr.medicine_name, mr.quantity, mr.cost, mr.remarks, a.tag_number
                    FROM Medicine_Record mr
                    JOIN Animal a ON mr.animal_id = a.animal_id
                    WHERE mr.animal_id = %s AND mr.date BETWEEN %s AND %s
                    ORDER BY mr.date DESC
                """, (animal_id, start_date, end_date))
            else:
                cursor.execute("""
                    SELECT mr.date, mr.medicine_name, mr.quantity, mr.cost, mr.remarks, a.tag_number
                    FROM Medicine_Record mr
                    JOIN Animal a ON mr.animal_id = a.animal_id
                    WHERE mr.date BETWEEN %s AND %s
                    ORDER BY mr.date DESC
                """, (start_date, end_date))
            
            medical_records = pd.DataFrame(cursor.fetchall())
            
            if not medical_records.empty:
                st.dataframe(medical_records, use_container_width=True)
                
                # Calculate total medical cost
                total_cost = medical_records['cost'].sum()
                st.metric("Total Medical Cost", f"${total_cost:,.2f}")
                
                # Plot medicine distribution
                if selected_animal_view != "All":
                    fig = px.bar(medical_records, x='medicine_name', y='cost',
                                title=f"Medicine Costs for {selected_animal_view}")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No medical records found for the selected period.")
            
            # Action buttons below the heading
            st.subheader("Actions")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("➕ Add Medical Record"):
                    st.session_state.show_add_medical = True
            
            with col2:
                if not medical_records.empty:
                    if st.button("✏️ Update Medical Record"):
                        st.session_state.show_update_medical = True
            
            # Add new medical record form
            if st.session_state.get('show_add_medical', False):
                with st.form("medical_form"):
                    st.subheader("Add New Medical Record")
                    selected_animal = st.selectbox("Select Animal", options=list(animal_options.keys()))
                    date = st.date_input("Date*")
                    medicine_name = st.text_input("Medicine Name*")
                    quantity = st.text_input("Quantity (e.g., 10ml)*")
                    cost = st.number_input("Cost ($)*", min_value=0.0, step=0.01)
                    remarks = st.text_area("Remarks")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Add Medical Record"):
                            if medicine_name and quantity and cost:
                                animal_id = animal_options[selected_animal]
                                try:
                                    cursor.execute("""
                                        INSERT INTO Medicine_Record (animal_id, date, medicine_name, quantity, cost, remarks)
                                        VALUES (%s, %s, %s, %s, %s, %s)
                                    """, (animal_id, date, medicine_name, quantity, cost, remarks))
                                    connection.commit()
                                    st.success("Medical record added successfully!")
                                    st.session_state.show_add_medical = False
                                    st.rerun()
                                except Error as e:
                                    st.error(f"Error adding medical record: {e}")
                            else:
                                st.error("Medicine name, quantity, and cost are required")
                    with col2:
                        if st.form_submit_button("Cancel"):
                            st.session_state.show_add_medical = False
            
            # Update medical record form
            if st.session_state.get('show_update_medical', False) and not medical_records.empty:
                with st.form("update_medical_form"):
                    st.subheader("Update Medical Record")
                    
                    selected_record = st.selectbox("Select Record to Update", 
                                                options=medical_records['date'].astype(str) + " - " + 
                                                medical_records['tag_number'] + " - " + 
                                                medical_records['medicine_name'])
                    
                    if selected_record:
                        parts = selected_record.split(" - ")
                        record_date = pd.to_datetime(parts[0]).date()
                        tag_number = parts[1]
                        medicine_name = parts[2]
                        
                        cursor.execute("""
                            SELECT mr.medicine_id, mr.quantity, mr.cost, mr.remarks
                            FROM Medicine_Record mr
                            JOIN Animal a ON mr.animal_id = a.animal_id
                            WHERE mr.date = %s AND a.tag_number = %s AND mr.medicine_name = %s
                        """, (record_date, tag_number, medicine_name))
                        record_data = cursor.fetchone()
                        
                        if record_data:
                            new_quantity = st.text_input("New Quantity", value=record_data['quantity'])
                            new_cost = st.number_input("New Cost ($)", 
                                                    min_value=0.0, 
                                                    step=0.01,
                                                    value=record_data['cost'])
                            new_remarks = st.text_area("New Remarks", value=record_data['remarks'] or "")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("Update Medical Record"):
                                    try:
                                        cursor.execute("""
                                            UPDATE Medicine_Record 
                                            SET quantity = %s, cost = %s, remarks = %s
                                            WHERE medicine_id = %s
                                        """, (new_quantity, new_cost, new_remarks, record_data['medicine_id']))
                                        connection.commit()
                                        st.success("Medical record updated successfully!")
                                        st.session_state.show_update_medical = False
                                        st.rerun()
                                    except Error as e:
                                        st.error(f"Error updating medical record: {e}")
                            with col2:
                                if st.form_submit_button("Cancel"):
                                    st.session_state.show_update_medical = False
            
        except Error as e:
            st.error(f"Error retrieving data: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

# Staff Management Page
elif page == "Staff Management":
    st.title("Staff Management")
    connection = create_connection()
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Display all staff
            st.subheader("All Staff Members")
            
            cursor.execute("SELECT * FROM Staff")
            staff = cursor.fetchall()
            
            if staff:
                cols = st.columns(3)
                for idx, staff_member in enumerate(staff):
                    with cols[idx % 3]:
                        st.markdown(f"""
                            <div class="animal-card">
                                <h3>{staff_member['name']}</h3>
                                <p><strong>Role:</strong> {staff_member['role']}</p>
                                <p><strong>Salary:</strong> ${staff_member['salary_per_month']:,.2f}/month</p>
                        """, unsafe_allow_html=True)
                        if staff_member['image']:
                            display_image(staff_member['image'])
                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("No staff members found.")
            
            # Action buttons below the heading
            st.subheader("Actions")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("➕ Add New Staff"):
                    st.session_state.show_add_staff = True
            
            with col2:
                if staff:
                    if st.button("✏️ Update Staff"):
                        st.session_state.show_update_staff = True
            
            with col3:
                if staff:
                    if st.button("🗑️ Delete Staff"):
                        st.session_state.show_delete_staff = True
            
            # Add new staff form
            if st.session_state.get('show_add_staff', False):
                with st.form("staff_form"):
                    st.subheader("Add New Staff Member")
                    name = st.text_input("Name*")
                    role = st.text_input("Role*")
                    salary = st.number_input("Monthly Salary ($)*", min_value=0.0, step=0.01)
                    image = st.file_uploader("Staff Photo", type=['jpg', 'jpeg', 'png'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Add Staff"):
                            if name and role and salary:
                                try:
                                    image_data = image.read() if image else None
                                    cursor.execute("""
                                        INSERT INTO Staff (name, role, salary_per_month, image)
                                        VALUES (%s, %s, %s, %s)
                                    """, (name, role, salary, image_data))
                                    connection.commit()
                                    st.success("Staff member added successfully!")
                                    st.session_state.show_add_staff = False
                                    st.rerun()
                                except Error as e:
                                    st.error(f"Error adding staff member: {e}")
                            else:
                                st.error("Name, role, and salary are required")
                    with col2:
                        if st.form_submit_button("Cancel"):
                            st.session_state.show_add_staff = False
            
            # Update staff form
            if st.session_state.get('show_update_staff', False) and staff:
                with st.form("edit_staff_form"):
                    st.subheader("Update Staff Member")
                    
                    staff_options = {f"{s['name']} (ID: {s['staff_id']})": s['staff_id'] for s in staff}
                    selected_staff = st.selectbox("Select Staff", options=list(staff_options.keys()))
                    
                    if selected_staff:
                        staff_id = staff_options[selected_staff]
                        cursor.execute("SELECT * FROM Staff WHERE staff_id = %s", (staff_id,))
                        staff_data = cursor.fetchone()
                        
                        new_name = st.text_input("Name", value=staff_data['name'])
                        new_role = st.text_input("Role", value=staff_data['role'])
                        new_salary = st.number_input(
                            "Monthly Salary ($)", 
                            min_value=0.0, 
                            step=0.01,
                            value=staff_data['salary_per_month']
                        )
                        new_image = st.file_uploader("Update Photo", type=['jpg', 'jpeg', 'png'])
                        
                        if staff_data['image']:
                            st.markdown("**Current Photo:**")
                            display_image(staff_data['image'])
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Update Staff"):
                                try:
                                    image_data = new_image.read() if new_image else staff_data['image']
                                    cursor.execute("""
                                        UPDATE Staff 
                                        SET name = %s, role = %s, salary_per_month = %s, image = %s
                                        WHERE staff_id = %s
                                    """, (new_name, new_role, new_salary, image_data, staff_id))
                                    connection.commit()
                                    st.success("Staff member updated successfully!")
                                    st.session_state.show_update_staff = False
                                    st.rerun()
                                except Error as e:
                                    st.error(f"Error updating staff member: {e}")
                        with col2:
                            if st.form_submit_button("Cancel"):
                                st.session_state.show_update_staff = False
            
            # Delete staff form
            if st.session_state.get('show_delete_staff', False) and staff:
                with st.form("delete_staff_form"):
                    st.subheader("Delete Staff Member")
                    st.warning("Warning: This action cannot be undone")
                    
                    staff_options = {f"{s['name']} (ID: {s['staff_id']})": s['staff_id'] for s in staff}
                    selected_staff = st.selectbox("Select Staff to Delete", options=list(staff_options.keys()))
                    
                    if selected_staff:
                        staff_id = staff_options[selected_staff]
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Delete Staff"):
                                try:
                                    cursor.execute("DELETE FROM Staff WHERE staff_id = %s", (staff_id,))
                                    connection.commit()
                                    st.success("Staff member deleted successfully!")
                                    st.session_state.show_delete_staff = False
                                    st.rerun()
                                except Error as e:
                                    st.error(f"Error deleting staff member: {e}")
                        with col2:
                            if st.form_submit_button("Cancel"):
                                st.session_state.show_delete_staff = False
            
        except Error as e:
            st.error(f"Error retrieving data: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

# Financial Overview Page
elif page == "Financial Overview":
    st.title("Financial Overview")
    connection = create_connection()
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Display expense summary
            st.subheader("Expense Summary")
            
            cursor.execute("SELECT * FROM Expense_Summary ORDER BY month DESC")
            expenses = pd.DataFrame(cursor.fetchall())
            
            if not expenses.empty:
                # Convert month to string if not datetime
                if not pd.api.types.is_datetime64_any_dtype(expenses['month']):
                    expenses['month'] = pd.to_datetime(expenses['month']).dt.strftime('%Y-%m')
                else:
                    expenses['month'] = expenses['month'].dt.strftime('%Y-%m')
                st.dataframe(expenses, use_container_width=True)
                
                # Expense trends chart
                st.subheader("Expense Trends")
                fig = px.line(expenses, x='month', y='total_expense',
                             title="Total Monthly Expenses",
                             markers=True)
                st.plotly_chart(fig, use_container_width=True)
                
                # Expense composition chart
                st.subheader("Expense Composition")
                fig = px.bar(expenses, x='month',
                            y=['total_feed_cost', 'total_medicine_cost',
                               'total_salaries', 'total_utilities', 'other_expenses'],
                            title="Expense Breakdown by Category",
                            labels={'value': 'Amount ($)', 'variable': 'Category'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No expense records found.")
            
            # Action buttons below the heading
            st.subheader("Actions")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("➕ Add Expense Summary"):
                    st.session_state.show_add_expense = True
            
            with col2:
                if not expenses.empty:
                    if st.button("✏️ Update Expense Summary"):
                        st.session_state.show_update_expense = True
            
            # Add new expense summary form
            if st.session_state.get('show_add_expense', False):
                with st.form("expense_form"):
                    st.subheader("Add New Expense Summary")
                    month = st.date_input("Month*")
                    feed_cost = st.number_input("Total Feed Cost ($)", min_value=0.0, step=0.01)
                    medicine_cost = st.number_input("Total Medicine Cost ($)", min_value=0.0, step=0.01)
                    salaries = st.number_input("Total Salaries ($)", min_value=0.0, step=0.01)
                    utilities = st.number_input("Total Utilities ($)", min_value=0.0, step=0.01)
                    other_expenses = st.number_input("Other Expenses ($)", min_value=0.0, step=0.01)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Add Expense Summary"):
                            total = feed_cost + medicine_cost + salaries + utilities + other_expenses
                            try:
                                cursor.execute("""
                                    INSERT INTO Expense_Summary 
                                    (month, total_feed_cost, total_medicine_cost, total_salaries, 
                                     total_utilities, other_expenses, total_expense)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                                """, (month, feed_cost, medicine_cost, salaries, utilities, other_expenses, total))
                                connection.commit()
                                st.success("Expense summary added successfully!")
                                st.session_state.show_add_expense = False
                                st.rerun()
                            except Error as e:
                                st.error(f"Error adding expense summary: {e}")
                    with col2:
                        if st.form_submit_button("Cancel"):
                            st.session_state.show_add_expense = False
            
            # Update expense summary form
            if st.session_state.get('show_update_expense', False) and not expenses.empty:
                with st.form("update_expense_form"):
                    st.subheader("Update Expense Summary")
                    
                    selected_month = st.selectbox("Select Month to Update", options=expenses['month'])
                    
                    cursor.execute("SELECT * FROM Expense_Summary WHERE month = %s", 
                                 (pd.to_datetime(selected_month),))
                    expense_data = cursor.fetchone()
                    
                    if expense_data:
                        new_feed = st.number_input("Feed Cost ($)", 
                                                 min_value=0.0, 
                                                 step=0.01,
                                                 value=expense_data['total_feed_cost'])
                        new_med = st.number_input("Medicine Cost ($)", 
                                                 min_value=0.0, 
                                                 step=0.01,
                                                 value=expense_data['total_medicine_cost'])
                        new_salaries = st.number_input("Salaries ($)", 
                                                      min_value=0.0, 
                                                      step=0.01,
                                                      value=expense_data['total_salaries'])
                        new_utils = st.number_input("Utilities ($)", 
                                                   min_value=0.0, 
                                                   step=0.01,
                                                   value=expense_data['total_utilities'])
                        new_other = st.number_input("Other Expenses ($)", 
                                                    min_value=0.0, 
                                                    step=0.01,
                                                    value=expense_data['other_expenses'])
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Update Expense Summary"):
                                try:
                                    total = new_feed + new_med + new_salaries + new_utils + new_other
                                    cursor.execute("""
                                        UPDATE Expense_Summary 
                                        SET total_feed_cost = %s, total_medicine_cost = %s, 
                                            total_salaries = %s, total_utilities = %s, 
                                            other_expenses = %s, total_expense = %s
                                        WHERE expense_id = %s
                                    """, (new_feed, new_med, new_salaries, new_utils, new_other, total, expense_data['expense_id']))
                                    connection.commit()
                                    st.success("Expense summary updated successfully!")
                                    st.session_state.show_update_expense = False
                                    st.rerun()
                                except Error as e:
                                    st.error(f"Error updating expense summary: {e}")
                        with col2:
                            if st.form_submit_button("Cancel"):
                                st.session_state.show_update_expense = False
            
            # Utility bills section
            st.subheader("Utility Bills")
            
            cursor.execute("SELECT * FROM Utility_Bill ORDER BY month DESC")
            utility_bills = pd.DataFrame(cursor.fetchall())
            
            if not utility_bills.empty:
                # Convert month to string if not datetime
                if not pd.api.types.is_datetime64_any_dtype(utility_bills['month']):
                    utility_bills['month'] = pd.to_datetime(utility_bills['month']).dt.strftime('%Y-%m')
                else:
                    utility_bills['month'] = utility_bills['month'].dt.strftime('%Y-%m')
                st.dataframe(utility_bills, use_container_width=True)
                
                # Utility costs chart
                st.subheader("Utility Costs by Type")
                fig = px.pie(utility_bills, names='type', values='amount',
                             title="Utility Cost Distribution")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No utility bills found.")
            
            # Action buttons below the heading
            st.subheader("Utility Actions")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("➕ Add Utility Bill"):
                    st.session_state.show_add_utility = True
            
            with col2:
                if not utility_bills.empty:
                    if st.button("✏️ Update Utility Bill"):
                        st.session_state.show_update_utility = True
            
            # Add new utility bill form
            if st.session_state.get('show_add_utility', False):
                with st.form("utility_form"):
                    st.subheader("Add New Utility Bill")
                    month = st.date_input("Bill Month*")
                    bill_type = st.selectbox("Bill Type*", ["Electricity", "Water", "Gas", "Internet", "Other"])
                    amount = st.number_input("Amount ($)*", min_value=0.0, step=0.01)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Add Utility Bill"):
                            try:
                                cursor.execute("""
                                    INSERT INTO Utility_Bill (month, type, amount)
                                    VALUES (%s, %s, %s)
                                """, (month, bill_type, amount))
                                connection.commit()
                                st.success("Utility bill added successfully!")
                                st.session_state.show_add_utility = False
                                st.rerun()
                            except Error as e:
                                st.error(f"Error adding utility bill: {e}")
                    with col2:
                        if st.form_submit_button("Cancel"):
                            st.session_state.show_add_utility = False
            
            # Update utility bill form
            if st.session_state.get('show_update_utility', False) and not utility_bills.empty:
                with st.form("update_utility_form"):
                    st.subheader("Update Utility Bill")
                    
                    selected_bill = st.selectbox("Select Bill to Update", 
                                               options=utility_bills['month'] + " - " + utility_bills['type'])
                    
                    if selected_bill:
                        parts = selected_bill.split(" - ")
                        bill_month = pd.to_datetime(parts[0]).date()
                        bill_type = parts[1]
                        
                        cursor.execute("""
                            SELECT bill_id, amount 
                            FROM Utility_Bill 
                            WHERE month = %s AND type = %s
                        """, (bill_month, bill_type))
                        bill_data = cursor.fetchone()
                        
                        if bill_data:
                            new_amount = st.number_input("New Amount ($)", 
                                                       min_value=0.0, 
                                                       step=0.01,
                                                       value=bill_data['amount'])
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("Update Utility Bill"):
                                    try:
                                        cursor.execute("""
                                            UPDATE Utility_Bill 
                                            SET amount = %s
                                            WHERE bill_id = %s
                                        """, (new_amount, bill_data['bill_id']))
                                        connection.commit()
                                        st.success("Utility bill updated successfully!")
                                        st.session_state.show_update_utility = False
                                        st.rerun()
                                    except Error as e:
                                        st.error(f"Error updating utility bill: {e}")
                            with col2:
                                if st.form_submit_button("Cancel"):
                                    st.session_state.show_update_utility = False
            
        except Error as e:
            st.error(f"Error retrieving data: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #6c757d; padding: 10px;">
        Farm Management System © 2025 | Developed with Streamlit and MySQL
    </div>
""", unsafe_allow_html=True)