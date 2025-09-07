CREATE TABLE Users (
    user_id INT PRIMARY KEY,
    name NVARCHAR(100),
    email NVARCHAR(100) UNIQUE
);

CREATE TABLE Products (
    product_id INT PRIMARY KEY,
    name NVARCHAR(100),
    price DECIMAL(10,2),
    stock_quantity INT
);

CREATE TABLE Orders (
    order_id INT PRIMARY KEY,
    user_id INT FOREIGN KEY REFERENCES Users(user_id),
    order_date DATETIME DEFAULT GETDATE()
);

CREATE TABLE OrderDetails (
    order_id INT FOREIGN KEY REFERENCES Orders(order_id),
    product_id INT FOREIGN KEY REFERENCES Products(product_id),
    quantity INT,
    PRIMARY KEY (order_id, product_id)
);
