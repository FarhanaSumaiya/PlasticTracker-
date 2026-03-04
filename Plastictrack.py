import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import sqlite3
import matplotlib
matplotlib.use('TkAgg')  # Set the backend before importing pyplot
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import json
from datetime import datetime, timedelta
import os

class PlasticTrackPlus:
    def __init__(self, root):
        self.root = root
        self.root.title("PlasticTrack+")
        self.root.geometry("1200x800")
        self.style = ttkb.Style(theme="darkly")
        
        # Initialize database and data
        self.init_db()
        self.load_product_catalog()
        
        # Create main container
        self.container = ttkb.Frame(root)
        self.container.pack(fill="both", expand=True)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Show tracker by default
        self.show_tracker()
    
    def init_db(self):
        """Initialize the SQLite database"""
        self.conn = sqlite3.connect('plastictrack.db')
        self.c = self.conn.cursor()
        
        # Create tables if they don't exist
        self.c.execute('''CREATE TABLE IF NOT EXISTS plastic_usage
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          date TEXT NOT NULL,
                          plastic_type TEXT NOT NULL,
                          amount REAL NOT NULL,
                          unit TEXT NOT NULL,
                          recyclable INTEGER NOT NULL,
                          notes TEXT)''')
        
        self.c.execute('''CREATE TABLE IF NOT EXISTS user_goals
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          goal_type TEXT NOT NULL,
                          target_amount REAL NOT NULL,
                          target_date TEXT,
                          created_at TEXT NOT NULL)''')
        
        self.conn.commit()
    
    def load_product_catalog(self):
        """Load the reusable product catalog"""
        try:
            with open('products.json', 'r') as f:
                self.product_catalog = json.load(f)
        except FileNotFoundError:
            # Default product catalog if file doesn't exist
            self.product_catalog = {
                "categories": ["Food", "Shopping", "Water", "Household"],
                "products": [
                    {
                        "id": 1,
                        "name": "Stainless Steel Water Bottle",
                        "category": "Water",
                        "description": "750ml leak-proof bottle with insulation",
                        "price": 24.99,
                        "plastic_saved": "5 bottles/month",
                        "image": "bottle.png"
                    },
                    {
                        "id": 2,
                        "name": "Reusable Shopping Tote",
                        "category": "Shopping",
                        "description": "Large cotton tote bag with reinforced handles",
                        "price": 12.99,
                        "plastic_saved": "30 bags/year",
                        "image": "tote.png"
                    }
                ]
            }
            with open('products.json', 'w') as f:
                json.dump(self.product_catalog, f, indent=4)
    
    def create_menu_bar(self):
        """Create the main menu bar"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Export Report", command=self.export_report)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Plastic Tracker", command=self.show_tracker)
        view_menu.add_command(label="Product Store", command=self.show_store)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def clear_frame(self):
        """Clear the current view"""
        for widget in self.container.winfo_children():
            widget.destroy()
    
    def show_tracker(self):
        """Show the plastic tracking interface"""
        self.clear_frame()
        
        # Create notebook for tabs
        notebook = ttkb.Notebook(self.container)
        notebook.pack(fill="both", expand=True)
        
        # Add tabs
        log_tab = ttkb.Frame(notebook)
        stats_tab = ttkb.Frame(notebook)
        goals_tab = ttkb.Frame(notebook)
        
        notebook.add(log_tab, text="Log Usage")
        notebook.add(stats_tab, text="Statistics")
        notebook.add(goals_tab, text="Goals")
        
        # Build each tab
        self.build_log_tab(log_tab)
        self.build_stats_tab(stats_tab)
        self.build_goals_tab(goals_tab)
    
    def build_log_tab(self, parent):
        """Build the plastic logging interface"""
        # Form frame
        form_frame = ttkb.LabelFrame(parent, text="Log Plastic Usage", padding=10)
        form_frame.pack(fill="x", padx=10, pady=10)
        
        # Date
        ttkb.Label(form_frame, text="Date:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.date_entry = ttkb.Entry(form_frame)
        self.date_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Plastic type
        ttkb.Label(form_frame, text="Plastic Type:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.type_combobox = ttkb.Combobox(form_frame, values=[
            "Bottle", "Bag", "Straw", "Container", "Utensils", "Packaging", "Other"
        ])
        self.type_combobox.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Amount
        ttkb.Label(form_frame, text="Amount:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.amount_entry = ttkb.Entry(form_frame)
        self.amount_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Unit
        ttkb.Label(form_frame, text="Unit:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.unit_combobox = ttkb.Combobox(form_frame, values=["grams", "items", "liters"])
        self.unit_combobox.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        # Recyclable
        ttkb.Label(form_frame, text="Recyclable:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.recyclable_var = tk.IntVar()
        ttkb.Checkbutton(form_frame, variable=self.recyclable_var).grid(row=4, column=1, sticky="w", padx=5, pady=5)
        
        # Notes
        ttkb.Label(form_frame, text="Notes:").grid(row=5, column=0, sticky="ne", padx=5, pady=5)
        self.notes_text = tk.Text(form_frame, height=4, width=30)
        self.notes_text.grid(row=5, column=1, sticky="w", padx=5, pady=5)
        
        # Submit button
        submit_btn = ttkb.Button(form_frame, text="Submit", command=self.submit_usage)
        submit_btn.grid(row=6, column=1, sticky="e", padx=5, pady=10)
        
        # Recent entries frame
        entries_frame = ttkb.LabelFrame(parent, text="Recent Entries", padding=10)
        entries_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Treeview for entries
        columns = ("date", "type", "amount", "unit", "recyclable", "notes")
        self.entries_tree = ttkb.Treeview(
            entries_frame, columns=columns, show="headings", height=10
        )
        
        # Configure columns
        self.entries_tree.heading("date", text="Date")
        self.entries_tree.heading("type", text="Type")
        self.entries_tree.heading("amount", text="Amount")
        self.entries_tree.heading("unit", text="Unit")
        self.entries_tree.heading("recyclable", text="Recyclable")
        self.entries_tree.heading("notes", text="Notes")
        
        self.entries_tree.column("date", width=100)
        self.entries_tree.column("type", width=100)
        self.entries_tree.column("amount", width=80)
        self.entries_tree.column("unit", width=80)
        self.entries_tree.column("recyclable", width=80)
        self.entries_tree.column("notes", width=200)
        
        # Add scrollbar
        scrollbar = ttkb.Scrollbar(entries_frame, orient="vertical", command=self.entries_tree.yview)
        self.entries_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.entries_tree.pack(fill="both", expand=True)
        
        # Load recent entries
        self.load_recent_entries()
    
    def submit_usage(self):
        """Submit new plastic usage to the database"""
        try:
            date = self.date_entry.get()
            plastic_type = self.type_combobox.get()
            amount = float(self.amount_entry.get())
            unit = self.unit_combobox.get()
            recyclable = self.recyclable_var.get()
            notes = self.notes_text.get("1.0", "end-1c")
            
            self.c.execute(
                "INSERT INTO plastic_usage (date, plastic_type, amount, unit, recyclable, notes) VALUES (?, ?, ?, ?, ?, ?)",
                (date, plastic_type, amount, unit, recyclable, notes)
            )
            self.conn.commit()
            
            # Clear form
            self.type_combobox.set('')
            self.amount_entry.delete(0, tk.END)
            self.unit_combobox.set('')
            self.recyclable_var.set(0)
            self.notes_text.delete("1.0", tk.END)
            
            # Refresh entries
            self.load_recent_entries()
            
            # Show success message
            ttkb.Label(self.container, text="Entry added successfully!", foreground="green").pack()
            self.root.after(2000, lambda: self.clear_frame())
            
        except ValueError:
            ttkb.Label(self.container, text="Please enter valid data", foreground="red").pack()
            self.root.after(2000, lambda: self.clear_frame())
    
    def load_recent_entries(self):
        """Load recent entries into the treeview"""
        # Clear existing entries
        for item in self.entries_tree.get_children():
            self.entries_tree.delete(item)
        
        # Get last 10 entries
        self.c.execute("SELECT date, plastic_type, amount, unit, recyclable, notes FROM plastic_usage ORDER BY date DESC LIMIT 10")
        rows = self.c.fetchall()
        
        for row in rows:
            recyclable = "Yes" if row[4] else "No"
            self.entries_tree.insert("", "end", values=(row[0], row[1], row[2], row[3], recyclable, row[5]))
    
    def build_stats_tab(self, parent):
        """Build the statistics tab with visualizations"""
        # Main frame
        main_frame = ttkb.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Time period selection
        period_frame = ttkb.Frame(main_frame)
        period_frame.pack(fill="x", pady=5)
        
        ttkb.Label(period_frame, text="Time Period:").pack(side="left", padx=5)
        
        self.period_var = tk.StringVar(value="month")
        periods = [("Last Week", "week"), ("Last Month", "month"), ("Last Year", "year"), ("All Time", "all")]
        
        for text, value in periods:
            ttkb.Radiobutton(period_frame, text=text, variable=self.period_var, 
                           value=value, command=self.update_stats).pack(side="left", padx=5)
        
        # Visualization frame
        viz_frame = ttkb.Frame(main_frame)
        viz_frame.pack(fill="both", expand=True)
        
        # Create figure for matplotlib
        self.figure = plt.Figure(figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=viz_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Initial update
        self.update_stats()
    
    def update_stats(self):
        """Update the statistics visualizations based on selected period"""
        period = self.period_var.get()
        end_date = datetime.now()
        
        if period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            start_date = end_date - timedelta(days=30)
        elif period == "year":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = datetime.min  # All time
        
        # Query data for the period
        self.c.execute(
            "SELECT plastic_type, SUM(amount) FROM plastic_usage WHERE date BETWEEN ? AND ? GROUP BY plastic_type",
            (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        )
        data = self.c.fetchall()
        
        if not data:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, "No data available for selected period", 
                   ha="center", va="center", fontsize=12)
            ax.axis('off')
            self.canvas.draw()
            return
        
        # Prepare data for plotting
        types = [item[0] for item in data]
        amounts = [item[1] for item in data]
        
        # Clear figure and create subplots
        self.figure.clear()
        
        # Pie chart
        ax1 = self.figure.add_subplot(121)
        ax1.pie(amounts, labels=types, autopct='%1.1f%%', startangle=90)
        ax1.set_title("Plastic Usage by Type")
        
        # Bar chart
        ax2 = self.figure.add_subplot(122)
        ax2.bar(types, amounts)
        ax2.set_title("Total Amount by Type")
        ax2.set_ylabel("Amount")
        ax2.tick_params(axis='x', rotation=45)
        
        # Adjust layout and draw
        self.figure.tight_layout()
        self.canvas.draw()
        
        # Show summary
        total = sum(amounts)
        summary_text = f"Total plastic used: {total:.2f} units"
        if hasattr(self, 'summary_label'):
            self.summary_label.config(text=summary_text)
        else:
            self.summary_label = ttkb.Label(self.container, text=summary_text)
            self.summary_label.pack()
    
    def build_goals_tab(self, parent):
        """Build the goals tracking interface"""
        # Goals frame
        goals_frame = ttkb.LabelFrame(parent, text="Set Reduction Goals", padding=10)
        goals_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Goal type
        ttkb.Label(goals_frame, text="Goal Type:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.goal_type_combobox = ttkb.Combobox(goals_frame, values=[
            "Total Plastic Reduction", "Specific Type Reduction", "Recyclable Percentage"
        ])
        self.goal_type_combobox.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Target amount
        ttkb.Label(goals_frame, text="Target Amount:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.target_amount_entry = ttkb.Entry(goals_frame)
        self.target_amount_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Target date
        ttkb.Label(goals_frame, text="Target Date:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.target_date_entry = ttkb.Entry(goals_frame)
        self.target_date_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.target_date_entry.insert(0, (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"))
        
        # Submit button
        submit_btn = ttkb.Button(goals_frame, text="Set Goal", command=self.submit_goal)
        submit_btn.grid(row=3, column=1, sticky="e", padx=5, pady=10)
        
        # Current goals frame
        current_goals_frame = ttkb.LabelFrame(parent, text="Current Goals", padding=10)
        current_goals_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Treeview for goals
        columns = ("type", "target", "date", "progress")
        self.goals_tree = ttkb.Treeview(
            current_goals_frame, columns=columns, show="headings", height=5
        )
        
        # Configure columns
        self.goals_tree.heading("type", text="Goal Type")
        self.goals_tree.heading("target", text="Target Amount")
        self.goals_tree.heading("date", text="Target Date")
        self.goals_tree.heading("progress", text="Progress")
        
        self.goals_tree.column("type", width=150)
        self.goals_tree.column("target", width=100)
        self.goals_tree.column("date", width=100)
        self.goals_tree.column("progress", width=150)
        
        # Add scrollbar
        scrollbar = ttkb.Scrollbar(current_goals_frame, orient="vertical", command=self.goals_tree.yview)
        self.goals_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.goals_tree.pack(fill="both", expand=True)
        
        # Load current goals
        self.load_current_goals()
    
    def submit_goal(self):
        """Submit a new reduction goal"""
        try:
            goal_type = self.goal_type_combobox.get()
            target_amount = float(self.target_amount_entry.get())
            target_date = self.target_date_entry.get()
            created_at = datetime.now().strftime("%Y-%m-%d")
            
            self.c.execute(
                "INSERT INTO user_goals (goal_type, target_amount, target_date, created_at) VALUES (?, ?, ?, ?)",
                (goal_type, target_amount, target_date, created_at)
            )
            self.conn.commit()
            
            # Clear form
            self.goal_type_combobox.set('')
            self.target_amount_entry.delete(0, tk.END)
            self.target_date_entry.delete(0, tk.END)
            self.target_date_entry.insert(0, (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"))
            
            # Refresh goals
            self.load_current_goals()
            
            # Show success message
            ttkb.Label(self.container, text="Goal set successfully!", foreground="green").pack()
            self.root.after(2000, lambda: self.clear_frame())
            
        except ValueError:
            ttkb.Label(self.container, text="Please enter valid data", foreground="red").pack()
            self.root.after(2000, lambda: self.clear_frame())
    
    def load_current_goals(self):
        """Load current goals into the treeview"""
        # Clear existing goals
        for item in self.goals_tree.get_children():
            self.goals_tree.delete(item)
        
        # Get active goals
        self.c.execute("SELECT goal_type, target_amount, target_date FROM user_goals WHERE target_date >= date('now')")
        rows = self.c.fetchall()
        
        for row in rows:
            # Calculate progress (simplified for example)
            progress = "25%"  # In a real app, this would calculate actual progress
            self.goals_tree.insert("", "end", values=(row[0], row[1], row[2], progress))
    
    def show_store(self):
        """Show the reusable product store"""
        self.clear_frame()
        
        # Main store frame
        store_frame = ttkb.Frame(self.container)
        store_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Filter frame
        filter_frame = ttkb.Frame(store_frame)
        filter_frame.pack(fill="x", pady=5)
        
        ttkb.Label(filter_frame, text="Filter by Category:").pack(side="left", padx=5)
        
        self.category_var = tk.StringVar()
        self.category_var.set("All")
        
        categories = ["All"] + self.product_catalog["categories"]
        for category in categories:
            ttkb.Radiobutton(
                filter_frame, text=category, variable=self.category_var,
                value=category, command=self.update_product_display
            ).pack(side="left", padx=5)
        
        # Products display frame
        products_frame = ttkb.Frame(store_frame)
        products_frame.pack(fill="both", expand=True)
        
        # Canvas and scrollbar for products
        self.products_canvas = tk.Canvas(products_frame)
        scrollbar = ttkb.Scrollbar(products_frame, orient="vertical", command=self.products_canvas.yview)
        self.scrollable_frame = ttkb.Frame(self.products_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.products_canvas.configure(
                scrollregion=self.products_canvas.bbox("all")
            )
        )
        
        self.products_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.products_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.products_canvas.pack(side="left", fill="both", expand=True)
        
        # Cart frame
        cart_frame = ttkb.LabelFrame(store_frame, text="Your Cart", padding=10)
        cart_frame.pack(fill="x", pady=10)
        
        # Treeview for cart
        self.cart_tree = ttkb.Treeview(
            cart_frame, columns=("product", "price", "qty"), show="headings", height=3
        )
        
        self.cart_tree.heading("product", text="Product")
        self.cart_tree.heading("price", text="Price")
        self.cart_tree.heading("qty", text="Quantity")
        
        self.cart_tree.column("product", width=200)
        self.cart_tree.column("price", width=100)
        self.cart_tree.column("qty", width=80)
        
        self.cart_tree.pack(fill="x")
        
        # Cart actions
        cart_actions_frame = ttkb.Frame(cart_frame)
        cart_actions_frame.pack(fill="x", pady=5)
        
        ttkb.Button(cart_actions_frame, text="Checkout", command=self.simulate_checkout).pack(side="right", padx=5)
        ttkb.Button(cart_actions_frame, text="Clear Cart", command=self.clear_cart).pack(side="right", padx=5)
        
        # Initialize cart
        self.cart = []
        
        # Initial product display
        self.update_product_display()
    
    def update_product_display(self):
        """Update the product display based on filters"""
        # Clear current products
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Get filtered products
        category = self.category_var.get()
        if category == "All":
            products = self.product_catalog["products"]
        else:
            products = [p for p in self.product_catalog["products"] if p["category"] == category]
        
        # Display products
        for i, product in enumerate(products):
            product_frame = ttkb.Frame(self.scrollable_frame, padding=10, relief="ridge", borderwidth=1)
            product_frame.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
            
            # Product image (placeholder)
            ttkb.Label(product_frame, text="[Image]").grid(row=0, column=0, rowspan=4, padx=5, pady=5)
            
            # Product info
            ttkb.Label(product_frame, text=product["name"], font=("Helvetica", 12, "bold")).grid(
                row=0, column=1, sticky="w", padx=5)
            
            ttkb.Label(product_frame, text=product["description"]).grid(
                row=1, column=1, sticky="w", padx=5)
            
            ttkb.Label(product_frame, text=f"Plastic saved: {product['plastic_saved']}").grid(
                row=2, column=1, sticky="w", padx=5)
            
            ttkb.Label(product_frame, text=f"${product['price']:.2f}", font=("Helvetica", 12, "bold")).grid(
                row=3, column=1, sticky="w", padx=5)
            
            # Add to cart button
            ttkb.Button(
                product_frame, text="Add to Cart", 
                command=lambda p=product: self.add_to_cart(p)
            ).grid(row=3, column=2, padx=5)
    
    def add_to_cart(self, product):
        """Add a product to the shopping cart"""
        # Check if product already in cart
        for item in self.cart:
            if item["id"] == product["id"]:
                item["quantity"] += 1
                self.update_cart_display()
                return
        
        # Add new product to cart
        self.cart.append({
            "id": product["id"],
            "name": product["name"],
            "price": product["price"],
            "quantity": 1
        })
        
        self.update_cart_display()
    
    def update_cart_display(self):
        """Update the cart display"""
        # Clear current cart items
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        # Add current items
        total = 0
        for item in self.cart:
            self.cart_tree.insert("", "end", values=(
                item["name"], f"${item['price']:.2f}", item["quantity"]
            ))
            total += item["price"] * item["quantity"]
        
        # Add total row
        self.cart_tree.insert("", "end", values=(
            "TOTAL", f"${total:.2f}", sum(item['quantity'] for item in self.cart)
        ))
    
    def clear_cart(self):
        """Clear the shopping cart"""
        self.cart = []
        self.update_cart_display()
    
    def simulate_checkout(self):
        """Simulate the checkout process"""
        if not self.cart:
            ttkb.Label(self.container, text="Your cart is empty!", foreground="red").pack()
            self.root.after(2000, lambda: self.clear_frame())
            return
        
        # In a real app, this would process payment
        # Here we just show a success message
        ttkb.Label(self.container, text="Order simulated successfully! Thank you for choosing sustainable products.", 
                 foreground="green").pack()
        
        # Clear cart after checkout
        self.cart = []
        self.update_cart_display()
        
        self.root.after(3000, lambda: self.clear_frame())
    
    def export_report(self):
        """Export a PDF report of plastic usage"""
        # Get data for the last month
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        self.c.execute(
            "SELECT plastic_type, SUM(amount), unit FROM plastic_usage "
            "WHERE date BETWEEN ? AND ? GROUP BY plastic_type, unit",
            (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        )
        usage_data = self.c.fetchall()
        
        # Create PDF
        filename = f"PlasticTrack_Report_{end_date.strftime('%Y%m')}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=letter)
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = styles["Title"]
        heading_style = styles["Heading2"]
        normal_style = styles["Normal"]
        
        # Content
        content = []
        
        # Title
        content.append(Paragraph("PlasticTrack+ Monthly Report", title_style))
        content.append(Spacer(1, 12))
        
        # Date range
        content.append(Paragraph(
            f"Report Period: {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}",
            normal_style
        ))
        content.append(Spacer(1, 24))
        
        # Usage summary
        content.append(Paragraph("Plastic Usage Summary", heading_style))
        
        if usage_data:
            # Create table data
            table_data = [["Type", "Amount", "Unit"]]
            total = 0
            
            for row in usage_data:
                table_data.append([row[0], str(row[1]), row[2]])
                total += row[1]
            
            table_data.append(["TOTAL", str(total), ""])
            
            # Create table
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            content.append(table)
            content.append(Spacer(1, 12))
            
            # Recommendations
            content.append(Paragraph("Recommendations", heading_style))
            
            # Simple recommendations based on usage
            recommendations = []
            for row in usage_data:
                if row[0] == "Bottle" and row[1] > 5:
                    recommendations.append(
                        f"• Consider switching to a reusable water bottle (saved {row[1]} bottles this month)")
                elif row[0] == "Bag" and row[1] > 10:
                    recommendations.append(
                        f"• Consider using reusable shopping bags (saved {row[1]} plastic bags this month)")
            
            if recommendations:
                for rec in recommendations:
                    content.append(Paragraph(rec, normal_style))
                    content.append(Spacer(1, 8))
            else:
                content.append(Paragraph("Great job! Your plastic usage is minimal.", normal_style))
        else:
            content.append(Paragraph("No usage data available for this period.", normal_style))
        
        # Build PDF
        doc.build(content)
        
        # Show success message
        ttkb.Label(self.container, text=f"Report exported as {filename}", foreground="green").pack()
        self.root.after(3000, lambda: self.clear_frame())
    
    def show_about(self):
        """Show the about dialog"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About PlasticTrack+")
        about_window.geometry("400x300")
        
        ttkb.Label(about_window, text="PlasticTrack+", font=("Helvetica", 16, "bold")).pack(pady=10)
        ttkb.Label(about_window, text="Version 1.0").pack()
        ttkb.Label(about_window, text="\nAn application to track plastic usage\nand promote sustainable alternatives").pack(pady=10)
        
        ttkb.Label(about_window, text="© 2023 EcoTech Solutions").pack(side="bottom", pady=10)
        
        close_btn = ttkb.Button(about_window, text="Close", command=about_window.destroy)
        close_btn.pack(pady=10)
    
    def on_closing(self):
        """Handle application closing"""
        self.conn.close()
        self.root.destroy()

# Run the application
if __name__ == "__main__":
    root = ttkb.Window()
    app = PlasticTrackPlus(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()