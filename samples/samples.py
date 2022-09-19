"""Python wrappers for Document AI message types."""

from dataclasses import dataclass, field
import re
import time
from typing import List

from google.cloud import documentai
from google.cloud.documentai_toolbox import DocumentWrapper


PROJECT_ID = "valiant-marker-319718"
LOCATION = "us"  # Format is 'us' or 'eu'
PROCESSOR_ID = "86bd7a6996805c20"  # Create processor in Cloud Console

# Format 'gs://input_bucket/directory'
GCS_INPUT_PREFIX = "gs://gal-cloud-samples/documentai/input"

# Format 'gs://output_bucket/directory'
GCS_OUTPUT_URI = "gs://gal-cloud-samples/documentai/output"

def batch_process():
    opts = {}
    if LOCATION == "eu":
        opts = {"api_endpoint": "eu-documentai.googleapis.com"}

    # Instantiates a client
    docai_client = documentai.DocumentProcessorServiceClient(client_options=opts)

    RESOURCE_NAME = docai_client.processor_path(PROJECT_ID, LOCATION, PROCESSOR_ID)

    # Cloud Storage URI for the Input Directory
    gcs_prefix = documentai.GcsPrefix(gcs_uri_prefix=GCS_INPUT_PREFIX)

    # Load GCS Input URI into Batch Input Config
    input_config = documentai.BatchDocumentsInputConfig(gcs_prefix=gcs_prefix)

    # Cloud Storage URI for Output directory
    gcs_output_config = documentai.DocumentOutputConfig.GcsOutputConfig(
        gcs_uri=GCS_OUTPUT_URI
    )

    # Load GCS Output URI into OutputConfig object
    output_config = documentai.DocumentOutputConfig(gcs_output_config=gcs_output_config)

    # Configure Process Request
    request = documentai.BatchProcessRequest(
        name=RESOURCE_NAME,
        input_documents=input_config,
        document_output_config=output_config,
    )

    # Batch Process returns a Long Running Operation (LRO)
    operation = docai_client.batch_process_documents(request)

    print(f"Waiting for operation {operation.operation.name} to complete...")
    operation.result()

    print("Document processing complete.")



def main() -> None:
    batch_process()
    
    # merged_document = DocumentWrapper(
    #     "gs://gal-cloud-samples/documentai/output/417983068761916085/0")
    
    # print(merged_document.pages[0].paragraphs)
    


if __name__ == "__main__":
  main()

