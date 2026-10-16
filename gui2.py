import tkinter as tk
from tkinter import ttk, messagebox
import db

class SelfCheckout:
    def __init__(self, root):
        self.root = root
        self.root.title("Culver's Self-Checkout")
        self.root.geometry("1250x1000")
        self.root.configure(bg="#005599")

        db.init_db()

        self.customer = None
        self.order_id = None
        self.cart = []
        self.total = 0.0
        self.menu_items = db.get_menu_items()
        self.categories = sorted(set(item["category"] for item in self.menu_items))

        self.create_header()
        self.create_customer_section()
        self.create_main_layout()
        self.create_footer()

    # Header
    def create_header(self):
        header = tk.Frame(self.root, bg="#003366", height=80)
        header.pack(fill="x", pady=(10, 0))
        header.pack_propagate(False)

        title = tk.Label(header, text="CULVER'S SELF‑CHECKOUT",
                         font=("Segoe UI", 26, "bold"), fg="white", bg="#003366")
        title.pack(pady=(5, 0))
        subtitle = tk.Label(header, text="Select your items and review your order below",
                            font=("Segoe UI", 12), fg="#CCCCCC", bg="#003366")
        subtitle.pack()

    # Customer lookup section
    def create_customer_section(self):
        frame = tk.LabelFrame(self.root, text="Customer Account Lookup",
                              font=("Segoe UI", 12, "bold"),
                              bg="#003366", fg="white", padx=10, pady=10)
        frame.pack(fill="x", padx=20, pady=10)

        tk.Label(frame, text="Email:", bg="#1E1E2F", fg="white").grid(row=0, column=0, sticky="w")
        self.email_entry = tk.Entry(frame, width=30, bg="#2A2A3D", fg="white", insertbackground="white")
        self.email_entry.grid(row=0, column=1, padx=5)
        lookup_btn = tk.Button(frame, text="Find Customer", bg="#007A3E", fg="white",
                               font=("Segoe UI", 10, "bold"), command=self.lookup_customer)
        lookup_btn.grid(row=0, column=2, padx=5)

        self.customer_label = tk.Label(frame, text="No customer selected", fg="#AAAAAA", bg="#1E1E2F")
        self.customer_label.grid(row=1, column=0, columnspan=3, sticky="w")
    #Customer backend 
    def lookup_customer(self):
        email = self.email_entry.get().strip()
        customer = db.get_customer_by_email(email)
        if customer:
            self.customer = customer
            self.order_id = db.create_order(customer["customerId"])
            self.customer_label.config(text=f"Customer: {customer['fullName']} | Points: {customer['pointsBalance']}")
            messagebox.showinfo("Customer Found", f"Welcome back, {customer['fullName']}!")
        else:
            messagebox.showerror("Not Found", "Customer not found. Please try again.")

    # Main layout
    def create_main_layout(self):
        main_frame = tk.Frame(self.root, bg="#003366")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Left panel: categories
        left_panel = tk.Frame(main_frame, bg="#003366", width=200)
        left_panel.pack(side="left", fill="y", padx=10)
        tk.Label(left_panel, text="Categories", font=("Segoe UI", 12, "bold"),
                 bg="#003366", fg="white").pack(pady=5)

        for cat in self.categories:
            btn = tk.Button(left_panel, text=cat, bg="#005696", fg="white",
                            font=("Segoe UI", 10, "bold"), relief="flat",
                            command=lambda c=cat: self.show_items(c))
            btn.pack(pady=5, fill="x")

        # Center panel: menu items
        center_panel = tk.LabelFrame(main_frame, text="Menu Items", font=("Segoe UI", 12, "bold"),
                                     bg="#1E1E2F", fg="white", padx=10, pady=10)
        center_panel.pack(side="left", fill="both", expand=True, padx=10)

        self.items_list = tk.Listbox(center_panel, height=15, bg="#005696", fg="white",
                                     selectbackground="#007A3E", font=("Segoe UI", 10))
        self.items_list.pack(fill="both", expand=True, pady=5)
        self.show_items(self.categories[0])

        add_btn = tk.Button(center_panel, text="Add to Cart", bg="#007A3E", fg="white",
                            font=("Segoe UI", 11, "bold"), relief="flat", command=self.add_to_cart)
        add_btn.pack(pady=10)

        # Right panel: cart
        right_panel = tk.LabelFrame(main_frame, text="Your Cart", font=("Segoe UI", 12, "bold"),
                                    bg="#1E1E2F", fg="white", padx=10, pady=10)
        right_panel.pack(side="right", fill="both", expand=True, padx=10)

        self.cart_list = tk.Listbox(right_panel, height=15, bg="#005696", fg="white",
                                    selectbackground="#CC0000", font=("Segoe UI", 10))
        self.cart_list.pack(fill="both", expand=True, pady=5)

        remove_btn = tk.Button(right_panel, text="Remove Selected", bg="#CC0000", fg="white",
                               font=("Segoe UI", 11, "bold"), relief="flat", command=self.remove_from_cart)
        remove_btn.pack(pady=10)

        # New Remove All button
        remove_all_btn = tk.Button(right_panel, text="Remove All", bg="#990000", fg="white",
                                   font=("Segoe UI", 11, "bold"), relief="flat", command=self.remove_all)
        remove_all_btn.pack(pady=5)

    def show_items(self, category):
        self.items_list.delete(0, tk.END)
        for item in self.menu_items:
            if item["category"] == category and item["available"]:
                self.items_list.insert(tk.END, f"{item['name']} - ${item['price']:.2f}")

    def add_to_cart(self):
        selection = self.items_list.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to add.")
            return
        category = self.categories[0]
        item = [i for i in self.menu_items if i["category"] == category][selection[0]]
        db.add_order_item(self.order_id, item["itemId"], 1, item["price"])
        self.cart.append(item)
        self.cart_list.insert(tk.END, f"{item['name']} - ${item['price']:.2f}")
        self.total += item["price"]
        self.update_total()

    def remove_from_cart(self):
        selection = self.cart_list.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to remove.")
            return
        index = selection[0]
        item = self.cart.pop(index)
        self.cart_list.delete(index)
        self.total -= item["price"]
        self.update_total()

    def remove_all(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Your cart is already empty.")
            return
        self.cart.clear()
        self.cart_list.delete(0, tk.END)
        self.total = 0.0
        self.update_total()

    def create_footer(self):
        footer = tk.Frame(self.root, bg="#003366", height=60)
        footer.pack(fill="x", pady=10)
        footer.pack_propagate(False)

        self.total_label = tk.Label(footer, text="Total: $0.00",
                                    font=("Segoe UI", 14, "bold"), fg="white", bg="#005696")
        self.total_label.pack(side="left", padx=20)

        checkout_btn = tk.Button(footer, text="Checkout", bg="#007A3E", fg="white",
                                 font=("Segoe UI", 12, "bold"), relief="flat", command=self.checkout)
        checkout_btn.pack(side="right", padx=20)

    def update_total(self):
        self.total_label.config(text=f"Total: ${self.total:.2f}")

    def checkout(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Your cart is empty.")
            return

        db.record_payment(self.order_id, self.total, "Card")
        messagebox.showinfo("Order Complete", f"Payment of ${self.total:.2f} recorded.\nThank you")
        self.root.destroy()  # closes the entire application window


if __name__ == "__main__":
    root = tk.Tk()
    app = SelfCheckout(root)
    root.mainloop()


