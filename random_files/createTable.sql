
CREATE TABLE U1 (
    email VARCHAR(100) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL
);
CREATE TABLE U2 (
    id INT PRIMARY KEY,
    email VARCHAR(100) NOT NULL
);

CREATE TABLE M1 (
    user_id INT PRIMARY KEY,
    goal VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE
);
CREATE TABLE M2 (
    id INT PRIMARY KEY,
    description TEXT,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE
);

CREATE TABLE Rp1 (
    recipe_name VARCHAR(100) PRIMARY KEY,
    category_name VARCHAR(100),
    prep_time INT,
    cook_time INT,
    serving_size INT,
    FOREIGN KEY (recipe_name) REFERENCES Recipe(name) ON DELETE CASCADE
);
CREATE TABLE Rp2 (
    id INT PRIMARY KEY,
    recipe_name VARCHAR(100)
);

CREATE TABLE R1 (
    user_id INT,
    recipe_id INT,
    content TEXT NOT NULL,
    rating INT NOT NULL,
    date_posted DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES Recipe(id) ON DELETE CASCADE
);
CREATE TABLE R2 (
    id INT PRIMARY KEY,
    user_id INT,
    recipe_id INT,
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES Recipe(id) ON DELETE CASCADE
);


CREATE TABLE I2 (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    recipe_id INT NOT NULL,
    nutritionalInfo_id INT NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES Recipe(id) ON DELETE CASCADE,
    FOREIGN KEY (nutritionalInfo_id) REFERENCES NutritionalInfo(id) ON DELETE CASCADE
);
CREATE TABLE I1 ( 
    name VARCHAR(100) PRIMARY KEY,
    recipe_id INT,
    quantity INT,
    unit_measurement VARCHAR(50),
    FOREIGN KEY (recipe_id) REFERENCES Recipe(id) ON DELETE CASCADE
);

CREATE TABLE N2 (
    id INT PRIMARY KEY,
    ingredient_id INT,
    FOREIGN KEY (ingredient_id) REFERENCES Ingredient(id) ON DELETE CASCADE
);
CREATE TABLE N1 (
    ingredient_id INT PRIMARY KEY,
    calories INT,
    protein INT,
    fat INT,
    fiber INT,
    carbohydrates INT,
    FOREIGN KEY (ingredient_id) REFERENCES Ingredient(id) ON DELETE CASCADE
);
