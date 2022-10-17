"""Python wrappers for Document AI message types."""

from atexit import register
from google.cloud.documentai_toolbox import Document

from google.cloud import documentai

import pandas as pd

from google.cloud.documentai_toolbox.wrappers import document


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

    # batch_process()
    # 1000 page -> 15597525561248170477
    # 100 page -> 13189533460497167727

    document.print_gcs_document_tree("gs://gal-cloud-samples/documentai/output")

    merged_document = Document.from_gcs_prefix(
        gcs_prefix="gs://gal-cloud-samples/documentai/output/13189533460497167727/1"
    )

    # shards = document_wrapper.get_document("gs://gal-cloud-samples/documentai/output/4416480632642051388/2")

    # # shards = document_wrapper.get_document("gs://gal-cloud-samples/documentai/output/4416480632642051388/3")
    # merged_document = DocumentWrapper(shards)

    page = merged_document.pages[0]

    for e in merged_document.entities:
        print(f"{e.type_} : {e.mention_text}")

    # for idx,page in enumerate(merged_document.pages):
    #     for tidx,table in enumerate(page.tables):
    #         df = table.to_dataframe()
    #         f = open(f"table-{idx}-{tidx}.csv","w")
    #         f.write(table.to_csv(dataframe=df))
    #         f.close

    # # CODE SAMPLE : Search for a specific table and export to csv
    # target_pages = merged_document.search_pages(target_string="Tax Invoice")
    # for page in target_pages:
    #     for table in page.tables:
    #         table.to_csv("data5.csv")


if __name__ == "__main__":
    main()
