"""
Car controllers for handling car-related operations
"""
from typing import List, Optional
from sqlmodel import Session, select, create_engine
from models import Car
from schemas import CarResponse
import os
from dotenv import load_dotenv

load_dotenv()

# Use the same database configuration as controllers
DATABASE_URL = os.getenv("DB_URL", "sqlite:///./autocare.db")
engine = create_engine(DATABASE_URL, echo=False)


def get_all_cars_controller() -> List[Car]:
    """Get all cars from database"""
    with Session(engine) as session:
        statement = select(Car)
        cars = session.exec(statement).all()
        import csv
        return cars


def get_car_by_id_controller(car_id: int) -> Optional[Car]:
    """Get car by ID"""
    with Session(engine) as session:
        return session.get(Car, car_id)


def get_cars_by_ids_controller(car_ids: List[int]) -> List[Car]:
    """Get multiple cars by their IDs"""
    with Session(engine) as session:
        statement = select(Car).where(Car.id.in_(car_ids))
        cars = session.exec(statement).all()
        return cars


def get_cars_for_comparison_controller(limit: int = 10) -> List[Car]:
    """Get limited cars for comparison with only essential data"""
    with Session(engine) as session:
        statement = select(Car).limit(limit)
        cars = session.exec(statement).all()
        return cars


def get_cars_by_model_controller(model_name: str) -> List[Car]:
    """Get cars by model name"""
    with Session(engine) as session:
        statement = select(Car).where(Car.model_name == model_name)
        cars = session.exec(statement).all()
        return cars


def get_cars_by_year_controller(year: int) -> List[Car]:
    """Get cars by year"""
    with Session(engine) as session:
        statement = select(Car).where(Car.model_year == year)
        cars = session.exec(statement).all()
        return cars


def get_cars_by_year_range_controller(start_year: int, end_year: int) -> List[Car]:
    """Get cars within a year range"""
    with Session(engine) as session:
        statement = select(Car).where(
            Car.model_year >= start_year,
            Car.model_year <= end_year
        )
        cars = session.exec(statement).all()
        return cars


def get_cars_by_price_range_controller(min_price: int, max_price: int) -> List[Car]:
    """Get cars within a price range"""
    with Session(engine) as session:
        statement = select(Car).where(
            Car.base_msrp_usd >= min_price,
            Car.base_msrp_usd <= max_price
        )
        cars = session.exec(statement).all()
        return cars


def get_cars_by_body_type_controller(body_type: str) -> List[Car]:
    """Get cars by body type"""
    with Session(engine) as session:
        statement = select(Car).where(Car.body_type == body_type)
        cars = session.exec(statement).all()
        return cars


def get_cars_by_drivetrain_controller(drivetrain: str) -> List[Car]:
    """Get cars by drivetrain"""
    with Session(engine) as session:
        statement = select(Car).where(Car.drivetrain == drivetrain)
        cars = session.exec(statement).all()
        return cars


def search_cars_controller(
    model_name: Optional[str] = None,
    year: Optional[int] = None,
    body_type: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    drivetrain: Optional[str] = None,
    engine_type: Optional[str] = None
) -> List[Car]:
    """Search cars with multiple filters"""
    with Session(engine) as session:
        statement = select(Car)
        
        if model_name:
            statement = statement.where(Car.model_name.ilike(f"%{model_name}%"))
        if year:
            statement = statement.where(Car.model_year == year)
        if body_type:
            statement = statement.where(Car.body_type.ilike(f"%{body_type}%"))
        if min_price:
            statement = statement.where(Car.base_msrp_usd >= min_price)
        if max_price:
            statement = statement.where(Car.base_msrp_usd <= max_price)
        if drivetrain:
            statement = statement.where(Car.drivetrain.ilike(f"%{drivetrain}%"))
        if engine_type:
            statement = statement.where(Car.engine_type.ilike(f"%{engine_type}%"))
        
        cars = session.exec(statement).all()
        return cars


def get_unique_models_controller() -> List[str]:
    """Get list of unique car models"""
    with Session(engine) as session:
        statement = select(Car.model_name).distinct()
        models = session.exec(statement).all()
        return sorted([model for model in models if model])


def get_unique_years_controller() -> List[int]:
    """Get list of unique car years"""
    with Session(engine) as session:
        statement = select(Car.model_year).distinct()
        years = session.exec(statement).all()
        return sorted([year for year in years if year])


def get_unique_body_types_controller() -> List[str]:
    """Get list of unique body types"""
    with Session(engine) as session:
        statement = select(Car.body_type).distinct()
        body_types = session.exec(statement).all()
        return sorted([bt for bt in body_types if bt])


def get_unique_drivetrains_controller() -> List[str]:
    """Get list of unique drivetrains"""
    with Session(engine) as session:
        statement = select(Car.drivetrain).distinct()
        drivetrains = session.exec(statement).all()
        return sorted([dt for dt in drivetrains if dt])


def convert_car_to_response(car: Car) -> CarResponse:
    """Convert Car model to CarResponse schema"""
    return CarResponse(
        id=car.id,
        model_name=car.model_name,
        model_year=car.model_year,
        trim_variant=car.trim_variant,
        body_type=car.body_type,
        length_mm=car.length_mm,
        width_mm=car.width_mm,
        height_mm=car.height_mm,
        wheelbase_mm=car.wheelbase_mm,
        curb_weight_kg=car.curb_weight_kg,
        engine_type=car.engine_type,
        displacement_cc=car.displacement_cc,
        cylinders=car.cylinders,
        horsepower_hp=car.horsepower_hp,
        torque_nm=car.torque_nm,
        transmission=car.transmission,
        drivetrain=car.drivetrain,
        acceleration_0_100_s=float(car.acceleration_0_100_s) if car.acceleration_0_100_s else None,
        top_speed_kmh=car.top_speed_kmh,
        fuel_consumption_combined=float(car.fuel_consumption_combined) if car.fuel_consumption_combined else None,
        co2_emissions=car.co2_emissions,
        electric_range_km=car.electric_range_km,
        infotainment=car.infotainment,
        safety_features=car.get_safety_features_list(),
        exterior_colors_available=car.get_exterior_colors_list(),
        interior_materials_colors=car.get_interior_colors_list(),
        wheel_sizes_available=car.get_wheel_sizes_list(),
        base_msrp_usd=car.base_msrp_usd,
        image_link=car.image_link,
        display_name=f"{car.model_year} {car.model_name} {car.trim_variant}"
    )


def convert_car_to_comparison_response(car: Car):
    """Convert Car model to lightweight CarComparisonResponse schema"""
    from schemas import CarComparisonResponse
    return CarComparisonResponse(
        id=car.id,
        model_name=car.model_name,
        model_year=car.model_year,
        trim_variant=car.trim_variant,
        body_type=car.body_type,
        base_msrp_usd=car.base_msrp_usd,
        display_name=f"{car.model_year} {car.model_name} {car.trim_variant}"
    )


def get_car_count_controller() -> int:
    """Get total count of cars in database"""
    with Session(engine) as session:
        statement = select(Car)
        cars = session.exec(statement).all()
        return len(cars)
