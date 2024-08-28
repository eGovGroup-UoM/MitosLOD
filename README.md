## MitosLOD project

**Overview**

The MitosLOD project aims to transform the Greek National Registry of Administrative Public Services (MITOS) into Linked Open Data (LOD) to significantly enhance transparency, efficiency, and accessibility of public services. By converting over 3,500 public service descriptions into a standardized, machine-readable format, MitosLOD seeks to simplify citizens' and businesses' interactions with government services, facilitate better decision-making, and promote the digital transformation of public administration in Greece. The result of the project is a dynamic, queryable endpoint for public service data, facilitating easy access and retrieval via open standards and semantic technologies like SPARQL (the standard query language and protocol for Linked Open Data on the web or for RDF triplestores). 


**Architecture**
*   **MITOS**: The Greek National Registry of Administrative Procedures.
*   **CPSV-AP**: Core Public Service Vocabulary Application Profile, a standard for describing public services as LOD.
*   **LOD**: Linked Open Data, an approach for publishing and connecting structured data on the web.
*   **Apache Airflow**: A platform for programmatically authoring, scheduling, and monitoring workflows.
*   **OpenLink Virtuoso**: An RDF triple store and SPARQL endpoint for storing and querying LOD.

![architecture_60pecentage](https://github.com/user-attachments/assets/8d84f50a-b310-4754-961d-04edd896e38b)

**Usage Scenarios**

*   **Improved Public Service Discoverability**: Citizens and businesses can easily find and understand available public services.
*   **Personalized Recommendations**: Service providers can offer targeted public service suggestions based on user needs.
*   **Policy Analysis**: Policymakers can evaluate the impact of public service changes.
*   **Transparency**: Public service information is openly accessible, promoting accountability.
*   **Performance Tracking**: Organizations can monitor and improve public service delivery.
*   **Value-added Services**: New applications and services can be developed using the LOD dataset.


**Project Structure**

*   `asyncMain.py`: Handles asynchronous retrieval of public service descriptions from the MITOS API.
*   `generated_data.ttl`: Stores the generated LOD data in Turtle syntax (RDF).
*   `mitos-transformation-dag.py`: Defines the Apache Airflow Directed Acyclic Graph (DAG) for orchestrating the data transformation pipeline.
*   `processorMain.py`: Processes, structures, and stores the retrieved public service descriptions in CSV files, organized by CPSV-AP classes.
*   `upload.py`: Manages the upload of the transformed LOD data to OpenLink Virtuoso.

**Dependencies**

*   Python 3.x
*   Apache Airflow
*   OpenLink Virtuoso
*   MITOS API Access

**Setup and Execution**

1.  **Clone the repository:**
    
    ```bash
    git clone https://github.com/BDTI-Mitos-LOD/cpsv-ap-transformation.git
    ```
    
2.  **Configure Airflow:**
    
    *   Set up an Airflow environment.
    *   Import the `mitos-transformation-dag.py` DAG into Airflow.
    *   Configure necessary Airflow connections (e.g., MITOS API, Virtuoso).
    
3.  **Run the Airflow DAG:**
    
    *   Trigger the DAG from the Airflow UI.
    *   The DAG will orchestrate the data retrieval, transformation, and upload to Virtuoso.
  
**Future Work**

*   Linking MITOS linked data with other LOD cloud data.
*   Creating user-friendly visualization tools for the LOD data.
*   Optimizing the LOD update process for efficiency.

**References**
1. Tambouris, E., Zeginis, D., Matziaras, G., Stefanidis, N., Promikyridis, R., Tarabanis, K., Oikonomou, D., Varlamis, I. & Bodino, M. C. (2024). Using the EU Big Data Test Infrastructure to Publish MITOS Public Service Descriptions as Linked Open Data. EGOV2024 – IFIP EGOV-CeDEM-EPART 2024. Available at: https://ceur-ws.org/Vol-3737/paper25.pdf

2. [BDTI story](https://big-data-test-infrastructure.ec.europa.eu/whats-new/news/mitoslod-pilot-story-transforming-greek-public-services-linked-open-data-2024-06-19_en)

**Acknowledgments**

*   The Big Data Test Infrastructure Support Team from the European Commission.
*   The GR digiGov-innoHUB project.

