"""
Test script to verify car controllers and data
"""
from car_controllers import (
    get_all_cars_controller, 
    get_cars_by_year_controller,
    get_cars_by_model_controller,
    search_cars_controller
)

def test_controllers():
    print("=== Testing Car Controllers ===")
    
    # Test get all cars
    all_cars = get_all_cars_controller()
    print(f"✓ Total cars in database: {len(all_cars)}")
    
    # Test get cars by year
    cars_2020 = get_cars_by_year_controller(2020)
    print(f"✓ Cars from 2020: {len(cars_2020)}")
    
    if cars_2020:
        car = cars_2020[0]
        print(f"\nSample 2020 car:")
        print(f"  - {car.model_year} {car.model_name} {car.trim_variant}")
        print(f"  - Price: ${car.base_msrp_usd:,}" if car.base_msrp_usd else "  - Price: Not specified")
        print(f"  - Engine: {car.engine_type}")
        print(f"  - HP: {car.horsepower_hp}")
        print(f"  - Body Type: {car.body_type}")
        print(f"  - Drivetrain: {car.drivetrain}")
        if car.acceleration_0_100_s:
            print(f"  - 0-100km/h: {car.acceleration_0_100_s}s")
    
    # Test get cars by model
    bmw_3_series = get_cars_by_model_controller("3 Series")
    print(f"\n✓ BMW 3 Series variants: {len(bmw_3_series)}")
    
    # Test search function
    search_results = search_cars_controller(
        year=2025,
        engine_type="Electric"
    )
    print(f"✓ Electric cars from 2025: {len(search_results)}")
    
    if search_results:
        for car in search_results:
            print(f"  - {car.model_year} {car.model_name} {car.trim_variant} (Electric)")
    
    print("\n=== All Tests Completed Successfully! ===")

if __name__ == "__main__":
    test_controllers()