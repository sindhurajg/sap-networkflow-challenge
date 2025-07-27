# sap-networkflow-challenge
This challenge requires implementing a full-stack analytics solution for Azure NSG flow logs: 
- Python ingestion and processing, Plotly Dash visualizations, containerized deployment, and Terraform-based infrastructure automation with CI/CD.

# parser.py:
- Read and decompress zipped CSV NSG flow-log files from an Azure Blob Storage container: currently they are downloaded to C:\Users\Admin\Downloads\NSG_Flow_Logs_files.
- Script parses are the CSV's from Zip files into single csv.

# dashboard.py:
Displays:
Bar chart for top 10 source IPs
Bar chart for top 10 destination IPs
Pie chart for top 10 denied flows
Time-series line chart of flows per hour
Heatmap for hourly traffic volume
Gauge or bullet chart for total flows and % denied
Table of top talkers and top listeners
Map visualization of geo-located source IPs
Sankey diagram of conversation flows between IP pairs
Text summary metrics (total flows, % denied, anomaly timestamps)

# dril_down.py:
Enable drill-down filtering by subscription, resource group, NSG, protocol, and time window.
