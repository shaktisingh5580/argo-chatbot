# backend/build_vector_store.py
import os
import glob
import xarray as xr
import pandas as pd
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

def process_metadata(file_path: str) -> dict:
    """Extracts key metadata from a single NetCDF file."""
    try:
        with xr.open_dataset(file_path) as ds:
            # Extracting relevant information, using .item() to get the scalar value
            wmo_id = ds['PLATFORM_NUMBER'].isel(N_PROF=0).values.item()
            project_name = ds.attrs.get('PROJECT_NAME', 'N/A').strip()
            
            # Find the range of dates
            start_date = pd.to_datetime(ds['JULD'].min().values).strftime('%Y-%m-%d')
            end_date = pd.to_datetime(ds['JULD'].max().values).strftime('%Y-%m-%d')
            
            # Find the geographic boundaries
            min_lat = ds['LATITUDE'].min().values.item()
            max_lat = ds['LATITUDE'].max().values.item()
            min_lon = ds['LONGITUDE'].min().values.item()
            max_lon = ds['LONGITUDE'].max().values.item()
            
            return {
                "wmo_id": int(wmo_id),
                "project_name": project_name,
                "date_range": f"{start_date} to {end_date}",
                "latitude_range": f"{min_lat:.2f} to {max_lat:.2f}",
                "longitude_range": f"{min_lon:.2f} to {max_lon:.2f}"
            }
    except Exception as e:
        # Print a helpful error message but continue with other files
        print(f"--> Skipping file {os.path.basename(file_path)} due to an error: {e}")
        return None

def main():
    """
    Scans the 'data' directory for NetCDF files, processes them, and adds their
    metadata to a persistent Chroma vector store in 'chroma_db'.
    """
    data_folder = 'data'
    persist_directory = 'chroma_db'
    
    # Check if the data folder exists
    if not os.path.isdir(data_folder):
        print(f"Error: Data folder '{data_folder}' not found.")
        print("Please create a 'data' folder inside your 'backend' directory and add your NetCDF (.nc) files to it.")
        return

    # Find all files ending with .nc in the data folder
    netcdf_files = glob.glob(os.path.join(data_folder, '*.nc'))
    if not netcdf_files:
        print(f"Warning: No NetCDF files (.nc) found in the '{data_folder}' directory.")
        return
        
    print(f"Found {len(netcdf_files)} NetCDF files to process.")
    
    all_documents = []
    all_metadatas = []

    # Loop through each file and process its metadata
    for file_path in netcdf_files:
        print(f"Processing: {os.path.basename(file_path)}...")
        metadata = process_metadata(file_path)
        
        if metadata:
            # Create a descriptive text document for this specific float
            float_document = f"""--- ARGO Float Information Document ---
WMO ID: {metadata['wmo_id']}
Project Name: {metadata['project_name']}
Data Collection Period: {metadata['date_range']}
Geographic Area of Operation: Latitude Range [{metadata['latitude_range']}], Longitude Range [{metadata['longitude_range']}]
Available Parameters: Temperature, Salinity, Pressure."""
            
            all_documents.append(float_document)
            all_metadatas.append({"source": os.path.basename(file_path), "wmo_id": metadata["wmo_id"]})

    if not all_documents:
        print("Could not generate any valid documents from the files. Aborting vector store creation.")
        return
        
    print(f"\nInitializing embedding model and vector store at '{persist_directory}'...")
    # Initialize the embedding model using the recommended package
    embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Initialize ChromaDB using the recommended package, pointing to the persistent directory
    vector_store = Chroma(
        collection_name="argo_float_metadata",
        embedding_function=embedding_function,
        persist_directory=persist_directory
    )
    
    print(f"Adding {len(all_documents)} new documents to the vector store...")
    # Add all the generated documents and their metadata to the vector store
    vector_store.add_texts(
        texts=all_documents,
        metadatas=all_metadatas
    )
    
    print(f"\n✅ Successfully processed and added documents to the Chroma vector database.")
    print(f"Vector store is saved and ready in the '{persist_directory}' directory.")

if __name__ == "__main__":
    main()