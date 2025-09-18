from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd

# Load your new dataset
csv = pd.read_csv("2000-25.csv")

# Initialize embeddings model
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

# Set database location
db_location = "./chroma_db"

# Check if we need to add documents
add_documents = not os.path.exists(db_location)

if add_documents:
    documents = []
    ids = []

    for i, row in csv.iterrows():
        # Build text content from your new columns
        content = f"""
        Model Name: {row['model_name']}
        Model Year: {row['model_year']}
        Trim / Variant: {row['trim_variant']}
        Body Type: {row['body_type']}
        Dimensions (LxWxH): {row['length_mm']} x {row['width_mm']} x {row['height_mm']} mm
        Wheelbase: {row['wheelbase_mm']} mm
        Curb Weight: {row['curb_weight_kg']} kg
        Exterior Colors: {row['exterior_colors_available']}
        Interior Materials & Colors: {row['interior_materials_colors']}
        Engine Type: {row['engine_type']}
        Displacement: {row['displacement_cc']} cc
        Cylinders: {row['cylinders']}
        Horsepower: {row['horsepower_hp']} hp
        Torque: {row['torque_nm']} Nm
        Transmission: {row['transmission']}
        Drivetrain: {row['drivetrain']}
        Acceleration (0-100 km/h): {row['acceleration_0_100_s']} s
        Top Speed: {row['top_speed_kmh']} km/h
        Fuel Consumption (Combined): {row['fuel_consumption_combined']}
        CO₂ Emissions: {row['co2_emissions']}
        Electric Range: {row['electric_range_km']} km
        Infotainment: {row['infotainment']}
        Safety Features: {row['safety_features']}
        Wheel Sizes Available: {row['wheel_sizes_available']}
        Base MSRP (USD): ${row['base_msrp_usd']}
        """

        # Create a LangChain Document
        document = Document(
            page_content=content.strip(),
            metadata={
                "model_name": row["model_name"],
                "model_year": row["model_year"],
                "body_type": row["body_type"],
            },
            id=str(i)
        )
        ids.append(str(i))
        documents.append(document)

# Initialize vector store
vector_store = Chroma(
    collection_name="bmw_car_data",
    persist_directory=db_location,
    embedding_function=embeddings
)

# Add documents if first time
if add_documents:
    vector_store.add_documents(documents, ids=ids)

# Create retriever
retriever = vector_store.as_retriever(search_kwargs={"k": 3})
