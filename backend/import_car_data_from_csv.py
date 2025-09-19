#!/usr/bin/env python3
"""
Script to import car data from CSV file into the database
"""
import csv
import os
import sys
from decimal import Decimal, InvalidOperation
from sqlmodel import SQLModel, create_engine, Session
from models import Car


def clean_numeric_value(value: str) -> str:
    """Clean numeric values by removing any non-numeric characters except decimal points"""
    if not value or value.strip() == '':
        return None
    
    # Remove any non-numeric characters except decimal points and negative signs
    cleaned = ''.join(char for char in value if char.isdigit() or char == '.' or char == '-')
    return cleaned if cleaned else None


def safe_int_conversion(value: str) -> int:
    """Safely convert string to integer"""
    if not value or value.strip() == '':
        return None
    
    cleaned = clean_numeric_value(value)
    if cleaned is None:
        return None
    
    try:
        return int(float(cleaned))  # Convert to float first to handle decimals, then to int
    except (ValueError, TypeError):
        return None


def safe_decimal_conversion(value: str) -> Decimal:
    """Safely convert string to Decimal"""
    if not value or value.strip() == '':
        return None
    
    cleaned = clean_numeric_value(value)
    if cleaned is None:
        return None
    
    try:
        return Decimal(cleaned)
    except (InvalidOperation, ValueError, TypeError):
        return None


def clean_string_value(value: str) -> str:
    """Clean string values by stripping whitespace and handling empty values"""
    if not value or value.strip() == '':
        return None
    return value.strip()


def create_car_from_row(row: dict) -> Car:
    """Create a Car object from a CSV row"""
    
    car = Car(
        # Basic information
        model_name=clean_string_value(row.get('model_name')),
        model_year=safe_int_conversion(row.get('model_year')),
        trim_variant=clean_string_value(row.get('trim_variant')),
        body_type=clean_string_value(row.get('body_type')),
        
        # Dimensions
        length_mm=safe_int_conversion(row.get('length_mm')),
        width_mm=safe_int_conversion(row.get('width_mm')),
        height_mm=safe_int_conversion(row.get('height_mm')),
        wheelbase_mm=safe_int_conversion(row.get('wheelbase_mm')),
        curb_weight_kg=safe_int_conversion(row.get('curb_weight_kg')),
        
        # Engine specifications
        engine_type=clean_string_value(row.get('engine_type')),
        displacement_cc=safe_int_conversion(row.get('displacement_cc')),
        cylinders=clean_string_value(row.get('cylinders')),
        horsepower_hp=safe_int_conversion(row.get('horsepower_hp')),
        torque_nm=safe_int_conversion(row.get('torque_nm')),
        
        # Drivetrain
        transmission=clean_string_value(row.get('transmission')),
        drivetrain=clean_string_value(row.get('drivetrain')),
        
        # Performance
        acceleration_0_100_s=safe_decimal_conversion(row.get('acceleration_0_100_s')),
        top_speed_kmh=safe_int_conversion(row.get('top_speed_kmh')),
        fuel_consumption_combined=safe_decimal_conversion(row.get('fuel_consumption_combined')),
        co2_emissions=safe_int_conversion(row.get('co2_emissions')),
        electric_range_km=safe_int_conversion(row.get('electric_range_km')),
        
        # Features
        infotainment=clean_string_value(row.get('infotainment')),
        safety_features=clean_string_value(row.get('safety_features')),
        wheel_sizes_available=clean_string_value(row.get('wheel_sizes_available')),
        
        # Colors
        exterior_colors_available=clean_string_value(row.get('exterior_colors_available')),
        interior_materials_colors=clean_string_value(row.get('interior_materials_colors')),
        
        # Pricing
        base_msrp_usd=safe_int_conversion(row.get('base_msrp_usd')),
        
        # Media
        image_link=clean_string_value(row.get('link'))
    )
    
    return car


def import_cars_from_csv(csv_file_path: str, database_url: str = "sqlite:///./autocare.db"):
    """Import cars from CSV file into the database"""
    
    # Create database engine
    engine = create_engine(database_url, echo=True)
    
    # Create all tables
    SQLModel.metadata.create_all(engine)
    
    imported_count = 0
    error_count = 0
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            # Read CSV with DictReader
            csv_reader = csv.DictReader(file)
            
            print(f"Found columns: {csv_reader.fieldnames}")
            
            with Session(engine) as session:
                for row_num, row in enumerate(csv_reader, start=2):  # Start from 2 since header is row 1
                    try:
                        # Skip empty rows
                        if not any(value.strip() for value in row.values() if value):
                            continue
                        
                        # Create car from row
                        car = create_car_from_row(row)
                        
                        # Validate required fields
                        if not car.model_name or not car.model_year or not car.trim_variant:
                            print(f"Row {row_num}: Missing required fields (model_name, model_year, or trim_variant)")
                            error_count += 1
                            continue
                        
                        # Check if car already exists
                        existing_car = session.query(Car).filter(
                            Car.model_name == car.model_name,
                            Car.model_year == car.model_year,
                            Car.trim_variant == car.trim_variant
                        ).first()
                        
                        if existing_car:
                            print(f"Row {row_num}: Car already exists - {car}")
                            continue
                        
                        # Add car to session
                        session.add(car)
                        imported_count += 1
                        
                        print(f"Row {row_num}: Added car - {car}")
                        
                    except Exception as e:
                        print(f"Row {row_num}: Error processing row - {e}")
                        print(f"Row data: {row}")
                        error_count += 1
                        continue
                
                # Commit all changes
                try:
                    session.commit()
                    print(f"\nImport completed successfully!")
                    print(f"Total cars imported: {imported_count}")
                    print(f"Total errors: {error_count}")
                    
                except Exception as e:
                    print(f"Error committing to database: {e}")
                    session.rollback()
                    return False
                        
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_file_path}")
        return False
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return False
    
    return True


def main():
    """Main function"""
    # Default CSV file path
    csv_file = "db_data.csv"
    
    # Check if CSV file exists
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found in current directory")
        sys.exit(1)
    
    print(f"Starting import from {csv_file}...")
    success = import_cars_from_csv(csv_file, "postgresql://postgres:abi123@localhost:5432/autocare")

    if success:
        print("Import completed successfully!")
        sys.exit(0)
    else:
        print("Import failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()