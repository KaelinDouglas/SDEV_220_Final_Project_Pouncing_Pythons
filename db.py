import sqlite3


###name of our db file
DB_NAME = "culvers_selfcheckout.db"  

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

###initializing our db 
def init_db():  
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
                                    ###Customer table created
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Customer (
                customerId INTEGER PRIMARY KEY AUTOINCREMENT,
                fullName TEXT NOT NULL,
                phoneNUMBER TEXT, 
                email TEXT UNIQUE NOT NULL
            );
            """)
                                    ###RewardsAccount table created
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS RewardsAccount (
                accountId INTEGER PRIMARY KEY AUTOINCREMENT,
                pointsBalance INTEGER DEFAULT 0,
                customerId INTEGER NOT NULL,
                FOREIGN KEY (customerId) REFERENCES Customer(customerId)
            );
            """)
                                    ###MenuItem table created 
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS MenuItem (
                itemId INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL, 
                price REAL NOT NULL,
                category TEXT NOT NULL,
                available INTEGER DEFAULT 1
            );
            """)
                                ###Order table created
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS "Order" (
                orderId INTEGER PRIMARY KEY AUTOINCREMENT,
                orderDate TEXT DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'Pending',
                total REAL DEFAULT 0.0,
                customerId INTEGER,
                FOREIGN KEY (customerId) REFERENCES Customer (customerId)
                );
                """)
                                ###OrderItem table created
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS OrderItem (
                orderItemId INTEGER PRIMARY KEY AUTOINCREMENT,
                orderId INTEGER NOT NULL, 
                itemId INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                customizations TEXT,
                lineTotal REAL NOT NULL,
                FOREIGN KEY (orderId) REFERENCES "Order"(orderId),
                FOREIGN KEY (itemId) REFERENCES MenuItem(itemId)
                );
                """)
                                ###Payment table created
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Payment (
                paymentId INTEGER PRIMARY KEY AUTOINCREMENT,
                orderId INTEGER NOT NULL,
                amount REAL NOT NULL,
                method TEXT NOT NULL,
                status TEXT DEFAULT 'Completed',
                FOREIGN KEY (orderId) REFERENCES "Order"(orderId)
                );
                """)
                              ###SelfCheckout table created
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS SelfCheckout (
                sessionId INTEGER PRIMARY KEY AUTOINCREMENT,
                customerId INTEGER,
                orderId INTEGER,
                FOREIGN KEY (customerId) REFERENCES Customer(customerId),
                FOREIGN KEY (orderId) REFERENCES "Order"(orderId)
                );
                """)


                              ###Our menu items I chose from culvers website for our menu
            cursor.execute("SELECT COUNT(*) FROM MenuItem;")
            if cursor.fetchone()[0] == 0:
                menu_data = [
                    ("ButterBurger Cheese Value Basket", 4.79, "Combo", 1),
                    ("Crispy Chicken Value Basket", 6.79, "Combo", 1),
                    ("Water", 0.00, "Drink", 1),
                    ("Coca Cola", 2.19, "Drink", 1),
                    ("Single scoop of chocolate Fresh Frozen Custard", 3.29, "Dessert", 1),
                    ("Single scoop of vanilla Fresh Frozen Custard", 3.29, "Dessert", 1),
                ]
                cursor.executemany(
                    "INSERT INTO MenuItem (name, price, category, available) VALUES (?,?,?,?);",
                    menu_data
                )


                              ###Our two test customers stored in the database for testing our app
            cursor.execute("SELECT COUNT(*) FROM Customer;")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                INSERT INTO Customer (fullName, phoneNumber, email)
                VALUES
                    ('Michael Myers', '812-303-0555', 'm.myers@halloween.com'),
                    ('Penny Wise', '812-228-6557', 'p.wise@halloween.com');
                """)

                cursor.execute("""
                INSERT INTO RewardsAccount (pointsBalance, customerId)
                VALUES
                    (100, 1),
                    (100, 2);
                """)
            conn.commit()
            print("db initialized!!")

    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")


###functions for GUI/my teammates to use
def get_menu_items() -> list[dict]:         ###Gets all available menu items formatted as dictionaries for the GUI
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM MenuItem WHERE available = 1;")
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Database error in get_menu_items: {e}")
        return []
    
def get_customer_by_email(email: str) -> dict |None:        ###Looks up test customer by email/returns their information/points
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    c.customerId,
                    c.fullName,
                    c.email,
                    c.phoneNumber,
                    r.pointsBalance
                FROM Customer c
                LEFT JOIN RewardsAccount r ON c.customerId = r.customerId
                WHERE LOWER(c.email) = LOWER(?);
            """, (email.strip(),))

            row = cursor.fetchone()
            return dict(row) if row else None
    except sqlite3.Error as e:
        print(f"Database error in get_customer_by_email: {e}")
        return None
    
def create_order(customer_id: int | None = None) -> int | None:     ###Creates new order record and returns generated orderId
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO \"Order\" (customerId, status, total) VALUES (?, 'Pending', 0.0);",
                (customer_id,)
            )
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Database error in create_order: {e}")
        return None

def add_order_item(order_id: int, item_id: int, quantity: int, price: float, customizations: str = "") -> bool:     ###Adds an item to the order and automatically updates the total price
    try:
        line_total = price * quantity
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO OrderItem (orderId, itemId, quantity, customizations, lineTotal)
                VALUES (?, ?, ?, ?, ?);
                """, (order_id, item_id, quantity, customizations, line_total))
            
            cursor.execute("""
                UPDATE "Order"
                SET total = (SELECT SUM(lineTotal) FROM OrderItem WHERE orderId = ?)
                WHERE orderId = ?;
            """, (order_id, order_id))

            conn.commit()
            return True
    except sqlite3.Error as e:
        print(f"Database error in add_order_item: {e}")
        return False
    
def record_payment(order_id: int, amount: float, method: str) -> bool:      ###Records payment and marks as paid
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO Payment (orderid, amount, method, status)
                VALUES (?, ?, ?, 'Completed');
            """, (order_id, amount, method))

            cursor.execute("""
                UPDATE "Order"
                SET status = 'Paid'
                WHERE orderId = ?;
            """, (order_id,))

            conn.commit()
            return True
    except sqlite3.Error as e:
        print(f"Database error in record_payment: {e}")
        return False



if __name__ == "__main__":
    # 1. Initialize tables and seed default data
    init_db()
