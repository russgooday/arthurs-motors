'''Tables SQL'''
MAKES = '''
CREATE TABLE makes (
    make_id INTEGER NOT NULL,
    make_name VARCHAR(50) NOT NULL,
    PRIMARY KEY (make_id)
)'''

MODELS = '''
CREATE TABLE models (
    model_id INTEGER NOT NULL,
    model_name VARCHAR(50) NOT NULL,
    make_id INTEGER,
    PRIMARY KEY (model_id),
    FOREIGN KEY(make_id) REFERENCES makes (make_id)
    ON DELETE CASCADE ON UPDATE CASCADE
)'''

COLOURS = '''
CREATE TABLE colours (
    colour_id INTEGER NOT NULL,
    colour VARCHAR(50) NOT NULL,
    PRIMARY KEY (colour_id)
)'''

FUEL_TYPES = '''
CREATE TABLE fuel_types (
    fuel_type_id INTEGER NOT NULL,
    fuel_type VARCHAR(50) NOT NULL,
    PRIMARY KEY (fuel_type_id)
)'''

TRANSMISSIONS = '''
CREATE TABLE transmissions (
    transmission_id INTEGER NOT NULL,
    transmission_type VARCHAR(50) NOT NULL,
    PRIMARY KEY (transmission_id)
)'''

CARS = '''
CREATE TABLE cars (
    vehicle_id INTEGER NOT NULL,
    make_id INTEGER NOT NULL,
    model_id INTEGER NOT NULL,
    colour_id INTEGER NOT NULL,
    fuel_type_id INTEGER NOT NULL,
    transmission_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    mileage INTEGER NOT NULL,
    PRIMARY KEY (vehicle_id),
    FOREIGN KEY(make_id) REFERENCES makes (make_id),
    FOREIGN KEY(model_id) REFERENCES models (model_id),
    FOREIGN KEY(colour_id) REFERENCES colours (colour_id),
    FOREIGN KEY(fuel_type_id) REFERENCES fuel_types (fuel_type_id),
    FOREIGN KEY(transmission_id) REFERENCES transmissions (transmission_id)
)'''
