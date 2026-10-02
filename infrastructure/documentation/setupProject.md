# PROJECT CONFIGURATION

1. Complete the `backend.hcl` file to store the backend in a remote location; in this case, we are using an S3 bucket. To do this, you must be authenticated in your terminal via the AWS CLI.

2. Run:
```bash
terraform init -backend-config="backend.hcl"
```
***Note: You must run these commands from the `/infrastructure` folder***

```bash
terraform plan
terraform apply
```

3. Run the job:
    1. Go to the Databricks environment UI -> **Jobs & pipelines** and select the job.
    2. Click the **Run now** button; this will download the data from the APIs.
    3. Go to a new workspace and create a new notebook.
    4. Run these scripts to verify the ingested news and OHLCV data:
    ```sql
    %sql
    -- Verify OHLCV data
    SELECT * FROM stonks_catalog.bronze.raw_ohlcv
    WHERE ticker = 'AAPL'
    ORDER BY date DESC
    LIMIT 10;

    %sql
    -- Verify news data
    SELECT * FROM stonks_catalog.bronze.raw_news
    LIMIT 10;
    ```
    5. ***Key consideration:** the first execution of the OHLCV job is configured for a *full* download to retrieve one year's worth of data.
    6. After the first execution, update line 108 to `outputsize="compact"` for daily retrieval:
    ```python
    # change to "compact" only for daily updates.
    pdf = fetch_alpha_vantage_daily(ticker, outputsize="full")
    ```