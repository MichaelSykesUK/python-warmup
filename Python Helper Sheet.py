# Python Helper Sheet

def save_to_parquet(df, file_path):
    """Save DataFrame to a Parquet file."""
    try:
        print("\nSaving to parquet")
        df.to_parquet(file_path, index=False)
        print(f"DataFrame successfully saved to '{file_path}'\n")
    except Exception as e:
        print(f"Error saving DataFrame to Parquet: {e}\n")
        raise


def save_to_csv(df, file_path, index):
    """Save DataFrame to a CSV file."""
    try:
        print("\nSaving to CSV")
        df.to_csv(file_path, index=index)
        print(f"DataFrame successfully saved to '{file_path}'")
    except Exception as e:
        print(f"Error saving DataFrame to CSV: {e}")
        raise


def read_file(file_path):
    """Read the certificate file."""
    with open(file_path.where(), "r") as fh:
        return fh.read()


def plot_time_series(ax_time, segment_data, param_data, param, segment_index):
    """Plot time series data."""
    ax_time.plot(
        segment_data.time,
        param_data,
        linestyle="-",
        linewidth=0.8,
        label=param,
    )
    ax_time.set_xlabel("Time")
    ax_time.set_ylabel(param)
    ax_time.set_title(f"Segment {segment_index}: {param} Time Series")
    ax_time.grid(True)
    ax_time.xaxis.set_major_formatter(
        mdates.DateFormatter("%d.%m.%y-%H:%M:%S"))
    plt.setp(ax_time.get_xticklabels(), rotation=45, ha="right")


time.sleep(retry_delay)

batch_size = initial_batch_size // (2**attempt)


query = (
    f"SELECT * FROM \"{table}\" WHERE time >= '{start_time_cursor}' "
    f"AND time <= '{end_time}' ORDER BY time LIMIT {batch_size}"
)

start_time_cursor = table_data_df["time"].iloc[-1] + pd.Timedelta(
    nanoseconds=1


except Exception as e:
    print(
        f"WARNING: Error querying table '{table}' with start time {start_time_cursor}: {e}"
    )
    raise


except Exception as e:
    print(f"Critical Error: Error querying table {table}: {e}")
    sys.exit(1)


table_data=client.query(query=query, language="sql").to_pandas()


num_cores=os.cpu_count()


print(
    f"Finished querying {completed}/{total_tables}: '{table}' "
    f"(Chunk {chunk_index}/{num_chunks} of chunk size: {chunk_size})"
)




logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

app=FastAPI(title="InfluxDB Query API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FILE_PATH=os.path.join(os.getcwd(), "file.txt")


@ app.get("/measurements")
def get_measurements():
    try:
        client=query_tools.read_certificate()
        client=query_tools.create_influxdb_client(
            token=query_tools.read_influxdb_credentials(CREDENTIALS_PATH)[
                "token"],
            host=query_tools.read_influxdb_credentials(CREDENTIALS_PATH)[
                "host"],
            database=query_tools.read_influxdb_credentials(CREDENTIALS_PATH)[
                "database"],
            cert=query_tools.read_certificate()
        )
        measurements=query_tools.query_influx_measurements(client)
        logger.info(f"Measurements: {measurements}")
        return {"measurements": measurements}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@ app.post("/query_table")
async def query_table_endpoint(query_params: QueryParams):
    try:
        client=query_tools.read_certificate()
        client=query_tools.create_influxdb_client(
            token=query_tools.read_influxdb_credentials(CREDENTIALS_PATH)[
                "token"],
            host=query_tools.read_influxdb_credentials(CREDENTIALS_PATH)[
                "host"],
            database=query_tools.read_influxdb_credentials(CREDENTIALS_PATH)[
                "database"],
            cert=query_tools.read_certificate()
        )
        table, df=query_tools.query_table_with_retries(
            client, query_params.table, query_params.start_time, query_params.end_time)
        dict_data=[OrderedDict((col, row[col])
                                 for col in df.columns) for _, row in df.iterrows()]
        return {"data": dict_data, "columns": list(df.columns)}
    except Exception as e:
        logger.error(f"Error querying data: {e}")
        raise HTTPException(status_code=500, detail=str(e))



def chunked(iterable, n):
    """Yield successive n-sized chunks from an iterable."""
    it=iter(iterable)
    while True:
        chunk=list(islice(it, n))
        if not chunk:
            break
        yield chunk


# Function to print loading bar
def print_loading_bar(progress):
    bar_length=40
    progress_length=int(bar_length * progress / 100)
    bar="|" + "=" * progress_length + "-" *
        (bar_length - progress_length) + "|"
    print(f"\r{bar} {progress} %", end="")
    sys.stdout.flush()


import datetime
import argparse
import pandas as pd
from typing import Tuple, Dict, List
import logging
from pandas.io.formats import excel


def setup_logging() -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        filename="iads_config_to_excel.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def read_iads_file(input_file: str) -> List[str]:
    """Reads an IADS config file and returns the content as a list of lines."""
    with open(input_file, 'r') as infile:
        return infile.readlines()


def parse_table_definition(line: str) -> List[str]:
    """Extracts column headers from the table definition line."""
    line=line.strip()[16:]  # Skip "TableDefinition "
    return ['TableDefinition'] + line.split("|")


def process_table_lines(lines: List[str]) -> Tuple[Dict[str, pd.DataFrame], List[str]]:
    """Processes lines of an IADS config file to extract tables and their data."""
    dfs_all: Dict[str, pd.DataFrame]={}
    found_tables: List[str]=[]
    table_data: List[List[str]]=[]
    column_headers: List[str]=[]
    current_table_name: str=""
    found_section=False

    for line in lines:
        if not found_section:
            if line.startswith("   Table "):
                found_section=True
                current_table_name=line[9:].strip()
                found_tables.append(current_table_name)
                print(f"Processing IADS table '{current_table_name}'...")
        elif line.startswith("   }"):
            # End of table
            dfs_all[current_table_name]=pd.DataFrame(
                table_data, columns=column_headers)
            table_data=[]
            column_headers=[]
            found_section=False
        elif line.startswith("      TableDefinition "):
            # Extract column headers
            column_headers=parse_table_definition(line)
        elif line and line.strip().split()[0] not in ("{", "}", "TableContents", "TableType"):
            # Process data rows
            column_1_data, remaining_data=line.strip().split(' ', 1)
            all_other_column_data=remaining_data.split('|')
            row_data=[column_1_data] + all_other_column_data
            table_data.append(row_data)

    return dfs_all, found_tables


def iads_df_to_excel(dfs_all: Dict[str, pd.DataFrame], found_tables: List[str]) -> None:
    """Outputs a dictionary of DataFrames to an Excel file."""
    current_datetime=datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file_name=f"iads_config_to_excel_{current_datetime}.xlsx"
    print(f"Creating output file '{output_file_name}'...")
    excel.ExcelFormatter.header_style=None

    try:
        with pd.ExcelWriter(output_file_name, engine="xlsxwriter") as writer:
            for table_name in found_tables:
                print(f"Creating sheet '{table_name}' in output file...")
                df=dfs_all[table_name]
                df.to_excel(
                    writer,
                    sheet_name=table_name[:31],
                    index=False,
                    header=True,
                    freeze_panes=(1, 0),
                )
                sheet=writer.sheets[table_name[:31]]
                num_columns=len(df.columns)
                left_align_format=writer.book.add_format({"align": "left"})
                sheet.set_column(0, num_columns - 1, None, left_align_format)
                sheet.autofilter(0, 0, 0, num_columns - 1)
                sheet.autofit()
        print(f"Output file '{output_file_name}' is complete.")
    except Exception as e:
        logging.error(f"Error creating output file '{output_file_name}'. "
                      f"Check log for details: {e}")


def main() -> None:
    """Run the main function of the script."""
    setup_logging()

    parser=argparse.ArgumentParser(
        description="This script outputs a single IADS config file to Excel"
    )
    parser.add_argument("input", help="Path to single IADS config file")
    args=parser.parse_args()

    try:
        lines=read_iads_file(args.input)
        dfs_all, found_tables=process_table_lines(lines)
        iads_df_to_excel(dfs_all, found_tables)
    except Exception as e:
        logging.error(
            f"Script failed. Check log file 'iads_config_to_excel.log' for details: {e}")


if __name__ == "__main__":
    main()


# Class for a customer logger
class CustomLogger:
    def __init__(self, enabled=False):
        self.enabled=enabled

    def debug(self, message):
        """Print debug message to console if logging is enabled."""
        if self.enabled:
            print(f"DEBUG: {message}")


df_1.columns=["timestamp_1", "param_key", "param_value_1"]

def load_datasets(self, input_file_1, input_file_2, time_adjust_1, time_adjust_2):
    """Loads datasets from csv of parquet."""

    print("\nLoading inputs files...")

    # Read input files
    input_file_1_type=basename(input_file_1).split(".")[-1].lower()
    input_file_2_type=basename(input_file_2).split(".")[-1].lower()
    if input_file_1_type == "csv":
        df_1=pd.read_csv(input_file_1, dtype={0: "int64", 1: "str"}, header=0)
    elif input_file_1_type == "parquet":
        df_1=pd.read_parquet(input_file_1)
        df_1[df_1.columns[0]]=df_1[df_1.columns[0]].astype("int64")
        df_1[df_1.columns[1]]=df_1[df_1.columns[1]].astype("str")
    else:
        raise ValueError(
            f"Unsupported file type for {input_file_1}: {input_file_1_type}")
    if input_file_2_type == "csv":
        df_2=pd.read_csv(input_file_2, dtype={0: "int64", 1: "str"}, header=0)
    elif input_file_2_type == "parquet":
        df_2=pd.read_parquet(input_file_2)
        df_2[df_2.columns[0]]=df_2[df_2.columns[0]].astype("int64")
        df_2[df_2.columns[1]]=df_2[df_2.columns[1]].astype("str")

    else:
        raise ValueError(
            f"Unsupported file type for {input_file_2}: {input_file_2_type}")

    # Rename columns
    df_1.columns=["timestamp_1", "param_key", "param_value_1"]
    df_2.columns=["timestamp_2", "param_key", "param_value_2"]
    self.logger.debug(df_1.head())
    self.logger.debug(df_2.head())

    # Get unique param keys in each dataset
    param_keys_1=set(df_1["param_key"])
    param_keys_2=set(df_2["param_key"])
    self.logger.debug(f"Dataset 1 'param_key' values:\n{param_keys_1}")
    self.logger.debug(f"Dataset 2 'param_key' values:\n{param_keys_2}")

    # Sort dataframes on Unix timestamp (ns)
    df_1=df_1.sort_values("timestamp_1").reset_index(drop=True)
    df_2=df_2.sort_values("timestamp_2").reset_index(drop=True)

    # Calculate the max and min time difference between df_1 and df_2
    timstamp_1_min=df_1["timestamp_1"].min()
    timestamp_2_min=df_2["timestamp_2"].min()
    timestamp_1_max=df_1["timestamp_1"].max()
    timestamp_2_max=df_2["timestamp_2"].max()
    timestamp_min=max(timstamp_1_min, timestamp_2_min)
    timestamp_max=min(timestamp_1_max, timestamp_2_max)
    if timestamp_min >= timestamp_max:
        print(
            f"\nWARNING: Time range min: {timestamp_min} > Time range max: {timestamp_max}")
        print(f"\nDataset 1, first row:\n{df_1.head(1)}")
        print(f"\nDataset 1, last row:\n{df_1.tail(1)}")
        print(f"\nDataset 2, first row:\n{df_2.head(1)}")
        print(f"\nDataset 2, last row:\n{df_2.tail(1)}\n")
        sys.exit(1)

    # Trim dataframes to have the similar start and end timestamps
    df_1=df_1[
        (df_1["timestamp_1"] >= timestamp_min) & (
            df_1["timestamp_1"] <= timestamp_max)
    ].reset_index(drop=True)
    df_2=df_2[
        (df_2["timestamp_2"] >= timestamp_min) & (
            df_2["timestamp_2"] <= timestamp_max)
    ].reset_index(drop=True)

    # Convert Unix timestamp datetime in new column
    df_1["timestamp_utc_1"]=pd.to_datetime(
        df_1["timestamp_1"], unit="ns").astype('str')
    df_2["timestamp_utc_2"]=pd.to_datetime(
        df_2["timestamp_2"], unit="ns").astype('str')

    # Calculate time delta from start
    df_1["time_delta_1"]=df_1["timestamp_1"] - df_1["timestamp_1"].iloc[0]
    df_2["time_delta_2"]=df_2["timestamp_2"] - df_2["timestamp_2"].iloc[0]

    # Adjust for time alignment (missing samples, lag etc.)
    df_1["time_delta_1"]=df_1["time_delta_1"] + (time_adjust_1 * 1e9)
    df_2["time_delta_2"]=df_2["time_delta_2"] + (time_adjust_2 * 1e9)

    print("Loading complete")

    return df_1, df_2

param_keys_1=set(df_1["param_key"])


def check_order(self, df_1, df_2):
    """Checks dataset order in preparation for dataframe merging."""

    print("Checking order...")

    # Group by param_key and calculate mean time intervals
    mean_delta_1_interval=(
        df_1.groupby("param_key")["timestamp_1"].apply(
            lambda x: (x - x.shift(1)).mean()).mean()
    )
    mean_delta_2_interval=(
        df_2.groupby("param_key")["timestamp_2"].apply(
            lambda x: (x - x.shift(1)).mean()).mean()
    )

    # Compare mean time intervals, switch DataFrames as necessary
    if mean_delta_1_interval > mean_delta_2_interval:
        switch=True
        df_1_temp=df_1.copy()
        df_2_temp=df_2.copy()
        df_1=df_2.copy()
        df_1.columns=df_1_temp.columns
        df_2=df_1_temp.copy()
        df_2.columns=df_2_temp.columns
        del df_1_temp
        del df_2_temp
    else:
        switch=False

    print("Checking order complete")

    # Convert Unix timestamp datetime in new column
    df_1["timestamp_1"]=df_1["timestamp_1"].astype('str')
    df_2["timestamp_2"]=df_2["timestamp_2"].astype('str')

    return df_1, df_2, mean_delta_1_interval, mean_delta_2_interval, switch

def remove_prefixes(self, df_1, df_2):
    """Removes common prefixes added by IADS or others."""

    print("Checking LRU prefixes...")

    # Define the list of prefixes to remove
    prefixes=["fcc1_", "fcc2_", "fcc3_", "lvsys_", "bis_", "wss_"]

    # Make specific columns lowercase to mitigate inconsistencies in datasets
    df_1["param_key"]=df_1["param_key"].str.lower()
    df_2["param_key"]=df_2["param_key"].str.lower()
    df_1["param_value_1"]=df_1["param_value_1"].astype(str).str.lower()
    df_2["param_value_2"]=df_2["param_value_2"].astype(str).str.lower()

    # Calculate lengths for customlog
    df_1_length=len(df_1["param_key"])
    df_2_length=len(df_2["param_key"])

    # Function to remove a prefix if it exists in all param_keys
    def remove_prefix(df, prefix):
        if df["param_key"].str.startswith(prefix).all():
            df["param_key"]=df["param_key"].str.replace(
                f"^{prefix}", "", regex=True)
            return True
        return False

    # Function to remove text before and including '__' in param_key
    def remove_text_before_double_underscore(df):
        df["param_key"]=df["param_key"].apply(
            lambda x: x.split('__', 1)[1] if '__' in x else x)

    # Check the presence of prefixes in df_1 and df_2
    prefix_info={}
    for prefix in prefixes:
        prefix_info[prefix]={
            "df_1": remove_prefix(df_1, prefix),
            "df_2": remove_prefix(df_2, prefix)
        }

    # Remove part leading up to and including '__' if present
    remove_text_before_double_underscore(df_1)
    remove_text_before_double_underscore(df_2)

    # Store the prefix removal information in a dictionary
    removed_info={
        "prefix_count_1": 0,
        "prefix_count_2": 0,
        "df_1_length": df_1_length,
        "df_2_length": df_2_length,
        "df_1_pre": any(prefix_info[prefix]["df_1"] for prefix in prefixes),
        "df_2_pre": any(prefix_info[prefix]["df_2"] for prefix in prefixes),
    }

    print("Checking prefixes complete")

    return df_1, df_2, removed_info

def check_params(self, df_1, df_2):
    """Checks datasets for inconsistencies."""

    print("Checking inconsistencies...")

    # Get unique param keys in each dataset
    param_keys_1=set(df_1["param_key"])
    param_keys_2=set(df_2["param_key"])
    self.logger.debug(f"Dataset 1 'param_key' values:\n{param_keys_1}")
    self.logger.debug(f"Dataset 2 'param_key' values:\n{param_keys_2}")

    # Common keys
    common_keys=param_keys_1 & param_keys_2
    if len(common_keys) < 1:
        print("ERROR: Datasets have no 'param_key' values in common. Nothing to compare.")
        sys.exit(1)
    else:
        print(f"Common 'param_key' values:\n{[k for k in common_keys]}")

    # Find param keys missing in each dataset
    missing_keys_1=param_keys_2 - param_keys_1
    missing_keys_2=param_keys_1 - param_keys_2

    # Remove rows with missing param keys
    df_1=df_1[df_1["param_key"].isin(common_keys)].copy()
    df_2=df_2[df_2["param_key"].isin(common_keys)].copy()

    # Convert Boolean to float
    bool_mapping={"False": 0, "True": 1, "false": 0, "true": 1}
    df_1["param_value_1"]=df_1["param_value_1"].replace(
        bool_mapping).astype(float)
    df_2["param_value_2"]=df_2["param_value_2"].replace(
        bool_mapping).astype(float)

    # Convert param_value columns to floats
    non_convertible_keys=set()

    def convert_to_float(x, param_key):
        try:
            return float(x)
        except ValueError:
            non_convertible_keys.add(param_key)
            return x

    df_1["param_value_1"]=df_1.apply(
        lambda row: convert_to_float(row["param_value_1"], row["param_key"]), axis=1
    )
    df_2["param_value_2"]=df_2.apply(
        lambda row: convert_to_float(row["param_value_2"], row["param_key"]), axis=1
    )

    # Record param value data types
    df_1["param_value_1_type"]=df_1["param_value_1"].apply(
        lambda x: type(x).__name__)
    df_2["param_value_2_type"]=df_2["param_value_2"].apply(
        lambda x: type(x).__name__)

    # Initialize mask to track rows with NaN values
    df_1_nans=df_1["param_value_1"].isna()
    df_2_nans=df_2["param_value_2"].isna()

    # Get filtered out param_key values
    param_key_1_nans=set(df_1[df_1_nans]["param_key"])
    param_key_2_nans=set(df_2[df_2_nans]["param_key"])

    # Count number of NaNs before dropping
    nans_df_1_before=df_1_nans.sum()
    nans_df_2_before=df_2_nans.sum()

    # Drop rows with NaN values
    df_1=df_1.dropna(subset=["param_value_1"])
    df_2=df_2.dropna(subset=["param_value_2"])

    # Count number of NaNs after dropping (should be 0)
    nans_df_1_after=df_1["param_value_1"].isna().sum()
    nans_df_2_after=df_2["param_value_2"].isna().sum()

    # Calculate number of rows dropped
    nans_dropped_df_1=nans_df_1_before - nans_df_1_after
    nans_dropped_df_2=nans_df_2_before - nans_df_2_after

    # Print the number of NaNs before, after, and how many were dropped
    self.logger.debug(
        f"Number of NaNs in df_1 before dropping: {nans_df_1_before}")
    self.logger.debug(
        f"Number of NaNs in df_2 before dropping: {nans_df_2_before}")
    self.logger.debug(f"Number of NaNs dropped from df_1: {nans_dropped_df_1}")
    self.logger.debug(f"Number of NaNs dropped from df_2: {nans_dropped_df_2}")
    self.logger.debug(
        f"Number of NaNs in df_1 after dropping: {nans_df_1_after}")
    self.logger.debug(
        f"Number of NaNs in df_2 after dropping: {nans_df_2_after}")

    print("Checking inconsistencies complete")

    return (
        df_1,
        df_2,
        missing_keys_1,
        missing_keys_2,
        param_key_1_nans,
        param_key_2_nans,
        non_convertible_keys,
    )


    def merge_datasets(self, df_1, df_2):
        """Merges datasets based on closest timestamp and matching param_key."""

        print("\nMerging datasets...")

        # Calculate the max and min time difference between df_1 and df_2
        time_delta_1_min=df_1["time_delta_1"].min()
        time_delta_2_min=df_2["time_delta_2"].min()
        time_delta_1_max=df_1["time_delta_1"].max()
        time_delta_2_max=df_2["time_delta_2"].max()
        time_delta_min=max(time_delta_1_min, time_delta_2_min)
        time_delta_max=min(time_delta_1_max, time_delta_2_max)

        # Define threshold (in nanoseconds)
        threshold=int(0.01e9)

        # Filter df_2 based on the max and min time difference and threshold
        df_2_filtered=df_2[
            (df_2["time_delta_2"] >= time_delta_min - threshold)
            & (df_2["time_delta_2"] <= time_delta_max + threshold)
        ]

        # Merge datasets
        df_merged=pd.merge_asof(
            df_2_filtered,
            df_1,
            left_on="time_delta_2",
            right_on="time_delta_1",
            by="param_key",
            direction="nearest",
        )

        # Rename columns
        df_merged.rename(
            columns={
                "time_delta_1": "time_delta_1n",
                "timestamp_1": "timestamp_1n",
                "timestamp_utc_1": "timestamp_utc_1n",
                "param_value_1": "param_value_1n",
                "param_value_1_type": "param_value_1n_type",
            },
            inplace=True,
        )

        # Record differences in data types
        df_type_diff=pd.DataFrame(columns=["param_key", "type_2", "type_1n"])
        for _, row in df_merged.iterrows():
            param_key=row["param_key"]
            type_1n=str(row["param_value_1n_type"])
            type_2=str(row["param_value_2_type"])
            if type_1n != type_2:
                df_type_diff=df_type_diff._append(
                    {"param_key": param_key, "type_2": type_2, "type_1n": type_1n},
                    ignore_index=True,
                )

        # Reorder columns
        desired_column_order=[
            "time_delta_2",
            "time_delta_1n",
            "timestamp_2",
            "timestamp_1n",
            "timestamp_utc_2",
            "timestamp_utc_1n",
            "param_key",
            "param_value_2",
            "param_value_1n",
            "param_value_2_type",
            "param_value_1n_type",
        ]

        df_merged=df_merged[desired_column_order]

        print("Merge complete")

        return df_merged, df_type_diff

    def compare_strings(self, value_1, value_2):
        """Compares param values that are strings."""

        if value_1 == value_2:
            return 100
        else:
            return 0

    def compare_values(self, value1, value2, param_range):
        """Compares param values that are floats."""

        try:
            min_range=float(param_range[0])
            max_range=float(param_range[1])
            range_span=max_range - min_range
            if range_span == 0:
                return 100
            value1_norm=(value1 - min_range) / range_span
            value2_norm=(value2 - min_range) / range_span
            comparison=(1 - abs(value1_norm - value2_norm)) * 100
            return comparison
        except (ValueError, TypeError, ZeroDivisionError) as e:
            print(
                f"""Error: {e}, value1: {value1}, value2:
                {value2}, param_range: {param_range}"""
            )
            return float("nan")

    def compare_analyses(self, value1, value2):
        """Compares other values."""

        min_value=min(abs(value1), abs(value2))
        max_value=max(abs(value1), abs(value2))
        if max_value == 0:
            return 100
        elif value1 * value2 <= 0:
            return 0
        else:
            return min_value / max_value * 100

    def analyse_data(self, df_merged):
        """Analyses merged data for sample accuracy."""

        print("Analysing data...")

        # Save each param value range of df_1n to a dictionary
        param_value_1n_min_max_dict=(
            df_merged.groupby("param_key")["param_value_1n"].agg(
                ["min", "max"]).to_dict()
        )

        # Compare param values
        param_value_compare=[]
        total_rows=len(df_merged)
        five_percent_step=total_rows // 20
        progress=0

        for i, (_, row) in enumerate(df_merged.iterrows(), 1):

            # Get row data
            param_key=row["param_key"]
            param_value_1n=row["param_value_1n"]
            param_value_2=row["param_value_2"]

            if isinstance(param_value_1n, str) and isinstance(param_value_2, str):

                comparison=self.compare_strings(param_value_1n, param_value_2)

            elif isinstance(param_value_1n, (float, int)) and isinstance(
                param_value_2, (float, int)
            ):

                # Convert to float if they are numeric
                param_value_1n=float(param_value_1n)
                param_value_2=float(param_value_2)

                # Get parameter value range
                param_value_1n_min=param_value_1n_min_max_dict["min"].get(
                    param_key)
                param_value_1n_max=param_value_1n_min_max_dict["max"].get(
                    param_key)

                if param_value_1n_min is not None and param_value_1n_max is not None:
                    param_value_1n_range=(
                        param_value_1n_min, param_value_1n_max)
                else:
                    param_value_1n_range=None
                    print(f"\nMissing range for: {param_key}")

                # Compare param values
                comparison=self.compare_values(
                    param_value_1n, param_value_2, param_value_1n_range
                )

            else:
                print(f"Param Key: {param_key}, Param Value 1n: "
                      f"{param_value_1n}, Param Value 2: {param_value_2}")
                raise ValueError(
                    f"""Unsupported parameter types for comparison at row {i}:
                    {type(param_value_1n)} and {type(param_value_2)}"""
                )

            # Append to list
            param_value_compare.append(math.floor(comparison))

            # Update loading bar
            if i % five_percent_step == 0 and i != total_rows:
                progress += 5
                print_loading_bar(progress)
            elif i == total_rows:
                progress=100
                print_loading_bar(progress)
                sys.stdout.write("\r\033[K\r")
                sys.stdout.flush()
                print("Analysis complete")

        # Add comparison results to DataFrame
        df_merged["param_value_compare"]=param_value_compare

        # Aggregate analyses
        param_key_list=[]
        param_value_accuracy_mean_list=[]
        param_value_accuracy_min_list=[]
        param_value_accuracy_max_list=[]
        param_value_2_mean_list=[]
        param_value_1n_mean_list=[]
        param_value_mean_accuracy_list=[]
        param_value_2_stan_dev_list=[]
        param_value_1n_stan_dev_list=[]
        stan_dev_accuracy_list=[]

        for param_key, param_data in df_merged.groupby("param_key"):

            # Param value accuracy
            param_value_accuracy_mean=math.floor(
                param_data["param_value_compare"].mean())
            param_value_accuracy_min=math.floor(
                param_data["param_value_compare"].min())
            param_value_accuracy_max=math.floor(
                param_data["param_value_compare"].max())

            # Mean value accuracy
            param_value_2_mean=param_data["param_value_2"].mean()
            param_value_1n_mean=param_data["param_value_1n"].mean()
            param_value_1n_min=param_value_1n_min_max_dict["min"].get(
                param_key)
            param_value_1n_max=param_value_1n_min_max_dict["max"].get(
                param_key)
            if param_value_1n_min is not None and param_value_1n_max is not None:
                param_value_1n_range=(param_value_1n_min, param_value_1n_max)
            else:
                param_value_1n_range=None
                print("Missing range for:\n", param_key)
            param_value_mean_accuracy=math.floor(
                self.compare_values(param_value_1n_mean,
                                    param_value_2_mean, param_value_1n_range)
            )

            # Standard deviation accuracy
            param_2_stan_dev=param_data["param_value_2"].std(ddof=1)
            param_1_stan_dev=param_data["param_value_1n"].std(ddof=1)
            stan_dev_accuracy=math.floor(
                self.compare_analyses(param_2_stan_dev, param_1_stan_dev)
            )

            # Append lists
            param_key_list.append(param_key)

            param_value_accuracy_mean_list.append(param_value_accuracy_mean)
            param_value_accuracy_min_list.append(param_value_accuracy_min)
            param_value_accuracy_max_list.append(param_value_accuracy_max)

            param_value_2_mean_list.append(param_value_2_mean)
            param_value_1n_mean_list.append(param_value_1n_mean)
            param_value_mean_accuracy_list.append(param_value_mean_accuracy)

            param_value_2_stan_dev_list.append(param_2_stan_dev)
            param_value_1n_stan_dev_list.append(param_1_stan_dev)
            stan_dev_accuracy_list.append(stan_dev_accuracy)

        # Create DataFrame of analyses
        df_analysis=pd.DataFrame(
            {
                "Parameter": param_key_list,
                "Mean of Param Sample Accuracy (%)": param_value_accuracy_mean_list,
                "Min of Param Sample Accuracy (%)": param_value_accuracy_min_list,
                "Max of Param Sample Accuracy (%)": param_value_accuracy_max_list,
                "Mean of Param Values (Dataset 2)": param_value_2_mean_list,
                "Mean of Param Values (Dataset 1n)": param_value_1n_mean_list,
                "Mean of Param Values Accuracy (%)": param_value_mean_accuracy_list,
                "Standard Deviation of Param Values (Dataset 2)": param_value_2_stan_dev_list,
                "Standard Deviation of Param Values (Dataset 1n)": param_value_1n_stan_dev_list,
                "Standard Deviation of Param Values Accuracy (%)": stan_dev_accuracy_list,
            }
        )

        return df_analysis

    # Summarise results
    def summarise_results(self, df_analysis):
        """Summarises the analysis for a summary sheet and terminal statement."""

        # Evaluate key results
        mean_of_mean_of_param_sample_accuracy=math.floor(
            df_analysis["Mean of Param Sample Accuracy (%)"].mean()
        )
        min_of_min_of_param_sample_accuracy=math.floor(
            df_analysis["Min of Param Sample Accuracy (%)"].min()
        )
        max_of_max_of_param_sample_accuracy=math.floor(
            df_analysis["Max of Param Sample Accuracy (%)"].max()
        )
        mean_of_mean_of_param_values_accuracy=math.floor(
            df_analysis["Mean of Param Values Accuracy (%)"].mean()
        )
        mean_of_stan_dev_of_param_values_accuracy=math.floor(
            df_analysis["Standard Deviation of Param Values Accuracy (%)"].mean(
            )
        )

        # Describe pass conditions
        pass_conditions=[
            "80-100% incl.",
            "0-100% incl.",
            "95-100% incl.",
            "90-100% incl.",
            "95-100% incl.",
        ]

        # Create DataFrame of summary results
        df_summary=pd.DataFrame(
            {
                "Mean of Mean of Param Sample Accuracy (%)": [
                    mean_of_mean_of_param_sample_accuracy
                ],
                "Min of Min of Param Sample Accuracy (%)": [min_of_min_of_param_sample_accuracy],
                "Max of Max of Param Sample Accuracy (%)": [max_of_max_of_param_sample_accuracy],
                "Mean of Mean of Param Values Accuracy (%)": [
                    mean_of_mean_of_param_values_accuracy
                ],
                "Mean of Standard Deviation of Param Values Accuracy (%)": [
                    mean_of_stan_dev_of_param_values_accuracy
                ],
            }
        )

        df_summary=df_summary.transpose()
        df_summary.columns=["Result %"]
        df_summary["Pass Condition"]=pass_conditions

        def pass_or_fail(row):
            """Determines pass or fail conditions."""
            condition=row["Pass Condition"]
            result=row["Result %"]
            if condition == "80-100% incl.":
                return "Pass" if 80 <= result <= 100 else "Fail"
            elif condition == "0-100% incl.":
                return "Pass" if 0 <= result <= 100 else "Fail"
            elif condition == "95-100% incl.":
                return "Pass" if 95 <= result <= 100 else "Fail"
            elif condition == "90-100% incl.":
                return "Pass" if 90 <= result <= 100 else "Fail"
            elif condition == "95-100% incl.":
                return "Pass" if 95 <= result <= 100 else "Fail"
            else:
                return ""

        # Apply the function to determine pass or fail
        df_summary["Pass or Fail"]=df_summary.apply(pass_or_fail, axis=1)
        pass_or_fail_values=df_summary["Pass or Fail"].tolist()
        overall_result="Pass" if all(
            value == "Pass" for value in pass_or_fail_values) else "Fail"

        # Table formats
        table_formats=[
            "plain",
            "simple",
            "github",
            "grid",
            "fancy_grid",
            "pipe",
            "orgtbl",
            "jira",
            "presto",
            "pretty",
        ]

        # Create analysis summary table
        table_format=table_formats[8]
        print("\nAnalysis Summary:")
        print(
            tabulate(
                df_summary,
                headers="keys",
                tablefmt=table_format,
                numalign="left",
                stralign="left",
            )
        )
        print(f"\nOverall result = {overall_result}")

        return df_summary, overall_result

    def create_plots(
        self,
        df_analysis,
        df_merged,
        output_dir,
        writer,
        current_datetime,
        include_param,
    ):
        """Creates plots from a random sample of parameters."""

        # Define plot params
        num_params_to_plot=36
        num_plots_per_sheet=12
        figsize=(18, 12)
        sheet_name="Sample Plots"

        # Unique param keys
        param_key=df_analysis["Parameter"].unique()

        # Convert param_key to a list for easier manipulation
        param_key_list=list(param_key)

        # Check if included param exists
        if include_param:
            if include_param not in param_key_list:
                raise ValueError(
                    f"'{include_param}' is not a valid parameter key.")

            # Remove include_param from the sampling pool to avoid duplication
            param_key_list.remove(include_param)

            # Limit the number of parameters to sample to the available size
            sample_size=min(num_params_to_plot - 1, len(param_key_list))

            # Sample param_key_list, excluding include_param
            param_key_subset=random.sample(param_key_list, sample_size)

            # Include the specified parameter at the start of the list
            param_key_subset.insert(0, include_param)
        else:
            # Limit the number of parameters to sample to the available size
            sample_size=min(num_params_to_plot, len(param_key_list))

            # Sample param_key_subset without include_param
            param_key_subset=random.sample(param_key_list, sample_size)

        # Calculate number of sheets needed
        num_sheets=math.ceil(len(param_key_subset) / num_plots_per_sheet)

        # Plots samples
        start_idx=0
        for i in range(num_sheets):

            end_idx=min(start_idx + num_plots_per_sheet, len(param_key_subset))
            param_key_sheet=param_key_subset[start_idx:end_idx]

            fig, axs=plt.subplots(3, 4, figsize=figsize)
            fig.suptitle(f"{sheet_name} {i + 1}")

            for j, param_key in enumerate(param_key_sheet):

                ax=axs[j // 4, j % 4]

                # Filter data for the current parameter
                param_data_merged=df_merged[df_merged["param_key"]
                    == param_key]

                # Convert time delta to seconds
                param_data_merged.loc[:, "time_delta_2"] /= 1e9
                param_data_merged.loc[:, "time_delta_1n"] /= 1e9

                # Check if the parameter is Boolean
                is_boolean=param_data_merged["param_value_2"].isin(
                    [0.0, 1.0]).all()

                # Plot data (can be customized for boolean or float)
                if is_boolean:
                    sns.lineplot(
                        x="time_delta_2",
                        y="param_value_2",
                        data=param_data_merged,
                        ax=ax,
                        label="Dataset 2",
                        color="blue",
                        linestyle="-",
                        linewidth=0.5,
                        drawstyle="steps-post",
                    )

                    sns.lineplot(
                        x="time_delta_1n",
                        y="param_value_1n",
                        data=param_data_merged,
                        ax=ax,
                        label="Dataset 1",
                        color="red",
                        linestyle="-",
                        linewidth=0.5,
                        drawstyle="steps-post",
                    )

                else:
                    sns.lineplot(
                        x="time_delta_2",
                        y="param_value_2",
                        data=param_data_merged,
                        ax=ax,
                        label="Dataset 2",
                        color="blue",
                        linestyle="-",
                        linewidth=0.5,
                        drawstyle="steps-post",
                    )

                    sns.lineplot(
                        x="time_delta_1n",
                        y="param_value_1n",
                        data=param_data_merged,
                        ax=ax,
                        label="Dataset 1",
                        color="red",
                        linestyle="-",
                        linewidth=0.5,
                        drawstyle="steps-post",
                    )

                # Set chart detail
                ax.set_title(param_key)
                ax.legend()
                ax.set_xlabel("Time Delta (s)")
                ax.set_ylabel("Param Value")

                if j == len(param_key_sheet) - 1:
                    for k in range(j + 1, num_plots_per_sheet):
                        axs[k // 4, k % 4].axis("off")

            plt.tight_layout(rect=[0, 0.03, 1, 0.95])

            # Ensure the plots directory exists in the root folder
            os.makedirs(f"{output_dir}/plots", exist_ok=True)

            # Save the figure as PNG in the plots directory
            plot_filename=f"{output_dir}/plots/plot_{i}_{current_datetime}.png"
            plt.savefig(plot_filename)

            # Insert the plot into the Excel file
            sheet_name_with_suffix=f"{sheet_name} {i + 1}" if num_sheets > 1 else sheet_name

            # Add plot to worksheet
            worksheet=writer.book.add_worksheet(sheet_name_with_suffix)
            writer.sheets[sheet_name_with_suffix]=worksheet
            worksheet.insert_image("A1", plot_filename)
            start_idx=end_idx

    def create_directories(self, input_file_1, input_file_2):
        """Creates directories for input and output data."""

        # Capture datetime for output file creation
        current_datetime=datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

        # Create output directory
        output_dir=f"output_dataset_compare/{current_datetime}"
        os.makedirs(output_dir, exist_ok=True)

        # Create output file name
        output_file_name=f"{output_dir}/output_dataset_compare_{current_datetime}.xlsx"

        # Create input directory
        input_data_dir=os.path.join(output_dir, "input_data")
        os.makedirs(input_data_dir, exist_ok=True)

        # Copy input files to input directory
        shutil.copy(input_file_1, input_data_dir)
        shutil.copy(input_file_2, input_data_dir)

        # Create writer
        writer=pd.ExcelWriter(output_file_name, engine="xlsxwriter")

        return current_datetime, output_dir, output_file_name, writer

    def split_dataframe(self, df, chunk_size):

        chunks=[df.iloc[i: i + chunk_size]
            for i in range(0, len(df), chunk_size)]

        return chunks

    def format_excel_sheet(self, writer, sheet, end_column):

        left_align_format=writer.book.add_format({"align": "left"})
        sheet.set_column(f"A:{end_column}", None, left_align_format)
        sheet.autofit()
        sheet.autofilter(f"A1:{end_column}1")

    def write_data_to_excel(self, writer, dataframe, sheet_name_prefix, formatting_letter):
        """Writes sheets to Excel."""

        max_rows_per_sheet=1048576

        if len(dataframe) > max_rows_per_sheet:
            chunks=self.split_dataframe(dataframe, max_rows_per_sheet)
            for i, chunk in enumerate(chunks):
                sheet_name=f"{sheet_name_prefix} Part {i + 1}"
                chunk.to_excel(
                    writer,
                    sheet_name=sheet_name,
                    index=False,
                    header=True,
                    freeze_panes=(1, 0),
                )
                self.format_excel_sheet(
                    writer, writer.sheets[sheet_name], formatting_letter)
        else:
            dataframe.to_excel(
                writer,
                sheet_name=sheet_name_prefix,
                index=False,
                header=True,
                freeze_panes=(1, 0),
            )
            self.format_excel_sheet(
                writer, writer.sheets[sheet_name_prefix], formatting_letter)

    def write_to_excel(
        self,
        df_summary,
        df_analysis,
        df_merged,
        include_param,
        overall_result,
        input_file_1,
        input_file_2,
        switch,
        missing_keys_1,
        missing_keys_2,
        df_type_diff,
    ):
        """Writes full analysis to Excel."""

        print("\nCreating output file...")

        # Get directories
        current_datetime, output_dir, output_file_name, writer=self.create_directories(
            input_file_1, input_file_2
        )

        # Convert timestamps greater than 15 digits (Excel limit) to string
        df_merged["timestamp_2"]=df_merged["timestamp_2"].astype(str)
        df_merged["timestamp_1n"]=df_merged["timestamp_1n"].astype(str)

        # Create a dictionary of summary data
        summary_data={
            (7, 0): "Overall Pass or Fail:",
            (7, 1): overall_result,
            (9, 0): "Input File 1:",
            (9, 1): input_file_1,
            (10, 0): "Input File 2:",
            (10, 1): input_file_2,
            (11, 0): "Files Switched:",
            (11, 1): switch,
            (12, 0): "Script Run Time",
            (14, 0): "Missing Parameters",
            (14, 3): "Inconsistent Param Value Types",
            (15, 0): "Missing in File 1",
            (15, 1): "Missing in File 2",
        }

        # Write the dictionary to the summary sheet
        print("Creating sheet, 'Analysis Summary'...")
        df_summary.to_excel(writer, sheet_name="Analysis Summary", index=True)

        # Add dictionary items
        summary_sheet=writer.sheets["Analysis Summary"]
        for (row, col), value in summary_data.items():
            summary_sheet.write(row, col, value)

        # Add missing keys, if any
        if not missing_keys_1:
            summary_sheet.write(16, 0, "None")
        else:
            for idx, key in enumerate(missing_keys_1):
                summary_sheet.write(16 + idx, 0, key)
        if not missing_keys_2:
            summary_sheet.write(16, 1, "None")
        else:
            for idx, key in enumerate(missing_keys_2):
                summary_sheet.write(16 + idx, 1, key)

        # Write data type differences from df_merged
        if df_type_diff.empty:
            summary_sheet.write(15, 3, "None")
        else:
            df_type_diff.to_excel(
                summary_sheet,
                startrow=15,
                startcol=3,
                index=False,
                header=["Parameter Name", "Type 2", "Type 1n"],
            )

        # Write other dataframes to workbook
        print("Creating sheet, 'Merged Data'...")
        self.write_data_to_excel(writer, df_merged, "Merged Data", "L")
        print("Creating sheet, 'Parameter Analysis'...")
        self.write_data_to_excel(
            writer, df_analysis, "Parameter Analysis", "J")

        # Create plots
        print("Creating sample plots...")
        self.create_plots(
            df_analysis, df_merged, output_dir, writer, current_datetime, include_param
        )

        # Calculate time taken and add to summary sheet
        time_taken=math.floor(time.time() - self.start_time)
        summary_sheet.write(12, 1, time_taken)
        summary_sheet.set_column(
            "A:D", None, writer.book.add_format({"align": "left"}))
        summary_sheet.autofit()

        # Close the writer
        writer.close()

        # Print completion message
        print("Output file complete")
        print(f"Output file = {output_file_name}")
        print(f"Script run time = {time_taken} seconds")
        print("\n")

    def main(self, args):

        # Store input arguments
        input_file_1=args.input_file_1
        input_file_2=args.input_file_2
        time_adjust_1=args.shift_1
        time_adjust_2=args.shift_2
        if args.include_param:
            include_param=args.include_param
        else:
            include_param=None

        # Load datasets
        df_1, df_2=self.load_datasets(
            input_file_1, input_file_2, time_adjust_1, time_adjust_2)

        # Check order
        df_1, df_2, mean_delta_1_interval, mean_delta_2_interval, switch=self.check_order(
            df_1, df_2
        )

        # Remove prefixes
        df_1, df_2, removed_info=self.remove_prefixes(df_1, df_2)

        # Check params
        (
            df_1,
            df_2,
            missing_keys_1,
            missing_keys_2,
            param_key_1_nans,
            param_key_2_nans,
            non_convertible_keys,
        )=self.check_params(df_1, df_2)

        # Load summary
        self.load_summary(
            mean_delta_1_interval,
            mean_delta_2_interval,
            input_file_1,
            input_file_2,
            switch,
            removed_info,
            param_key_1_nans,
            param_key_2_nans,
            missing_keys_1,
            missing_keys_2,
            non_convertible_keys,
        )

        # Merge datasets
        df_merged, df_type_diff=self.merge_datasets(df_1, df_2)

        # Analyse data
        df_analysis=self.analyse_data(df_merged)

        # Summarise results
        df_summary, overall_result=self.summarise_results(df_analysis)

        # Write merged dataset, analysis, and results to Excel
        self.write_to_excel(
            df_summary,
            df_analysis,
            df_merged,
            include_param,
            overall_result,
            input_file_1,
            input_file_2,
            switch,
            missing_keys_1,
            missing_keys_2,
            df_type_diff,
        )


def run():
    parser=argparse.ArgumentParser(
        description="""Compares the accuracy
                                     of two datasets."""
    )
    parser.add_argument(
        "input_file_1",
        type=str,
        help="""Input file 1 in .csv or parquet
                          format: time, param, value. Can handle header or no header.""",
    )
    parser.add_argument(
        "input_file_2",
        type=str,
        help="""Input file 2 in .csv or parquet
                          format: time, param, value. Can handle header or no header.""",
    )
    parser.add_argument(
        "--shift_1", "-s1",
        type=float,
        default=0,
        help="""Input file 1 time adjustment in seconds
                          (e.g., to align samples using 0.2s offset).
                            Default=0""",
    )
    parser.add_argument(
        "--shift_2", "-s2",
        type=float,
        default=0,
        help="""Input file 2 time adjustment in seconds
                          (e.g., to align samples using 0.2s offset).
                            Default=0""",
    )
    parser.add_argument(
        "--include_param", "-i",
        type=str,
        default=None,
        help="""Parameter to include in sample plots.""",
    )
    parser.add_argument(
        "--debug", "-d",
        action='store_true',
        help="""Enable debug statements.""",
    )

    args=parser.parse_args()

    # Create logger instance with debug enabled if the flag is set
    logger_instance=CustomLogger(enabled=args.debug)

    # Check files exist
    if not os.path.exists(args.input_file_1):
        print(f"File {args.input_file_1} does not exist.")
        return
    if not os.path.exists(args.input_file_2):
        print(f"File {args.input_file_2} does not exist.")
        return

    # Instantiate the DatasetCompare with the logger
    dataset_compare=DatasetCompare(logger=logger_instance)

    # Call main method
    dataset_compare.main(args)


if __name__ == "__main__":
    run()


another way to parse

    def merge_datasets(self, df_1, df_2):
        """Merges datasets based on closest timestamp and matching param_key."""

        print("\nMerging datasets...")

        # Calculate the max and min time difference between df_1 and df_2
        time_delta_1_min=df_1["time_delta_1"].min()
        time_delta_2_min=df_2["time_delta_2"].min()
        time_delta_1_max=df_1["time_delta_1"].max()
        time_delta_2_max=df_2["time_delta_2"].max()
        time_delta_min=max(time_delta_1_min, time_delta_2_min)
        time_delta_max=min(time_delta_1_max, time_delta_2_max)

        # Define threshold (in nanoseconds)
        threshold=int(0.01e9)

        # Filter df_2 based on the max and min time difference and threshold
        df_2_filtered=df_2[
            (df_2["time_delta_2"] >= time_delta_min - threshold)
            & (df_2["time_delta_2"] <= time_delta_max + threshold)
        ]

        # Merge datasets
        df_merged=pd.merge_asof(
            df_2_filtered,
            df_1,
            left_on="time_delta_2",
            right_on="time_delta_1",
            by="param_key",
            direction="nearest",
        )

        # Rename columns
        df_merged.rename(
            columns={
                "time_delta_1": "time_delta_1n",
                "timestamp_1": "timestamp_1n",
                "timestamp_utc_1": "timestamp_utc_1n",
                "param_value_1": "param_value_1n",
                "param_value_1_type": "param_value_1n_type",
            },
            inplace=True,
        )

        # Record differences in data types
        df_type_diff=pd.DataFrame(columns=["param_key", "type_2", "type_1n"])
        for _, row in df_merged.iterrows():
            param_key=row["param_key"]
            type_1n=str(row["param_value_1n_type"])
            type_2=str(row["param_value_2_type"])
            if type_1n != type_2:
                df_type_diff=df_type_diff._append(
                    {"param_key": param_key, "type_2": type_2, "type_1n": type_1n},
                    ignore_index=True,
                )

        # Reorder columns
        desired_column_order=[
            "time_delta_2",
            "time_delta_1n",
            "timestamp_2",
            "timestamp_1n",
            "timestamp_utc_2",
            "timestamp_utc_1n",
            "param_key",
            "param_value_2",
            "param_value_1n",
            "param_value_2_type",
            "param_value_1n_type",
        ]

        df_merged=df_merged[desired_column_order]

        print("Merge complete")

        return df_merged, df_type_diff

    def compare_strings(self, value_1, value_2):
        """Compares param values that are strings."""

        if value_1 == value_2:
            return 100
        else:
            return 0

    def compare_values(self, value1, value2, param_range):
        """Compares param values that are floats."""

        try:
            min_range=float(param_range[0])
            max_range=float(param_range[1])
            range_span=max_range - min_range
            if range_span == 0:
                return 100
            value1_norm=(value1 - min_range) / range_span
            value2_norm=(value2 - min_range) / range_span
            comparison=(1 - abs(value1_norm - value2_norm)) * 100
            return comparison
        except (ValueError, TypeError, ZeroDivisionError) as e:
            print(
                f"""Error: {e}, value1: {value1}, value2:
                {value2}, param_range: {param_range}"""
            )
            return float("nan")

    def compare_analyses(self, value1, value2):
        """Compares other values."""

        min_value=min(abs(value1), abs(value2))
        max_value=max(abs(value1), abs(value2))
        if max_value == 0:
            return 100
        elif value1 * value2 <= 0:
            return 0
        else:
            return min_value / max_value * 100

    def analyse_data(self, df_merged):
        """Analyses merged data for sample accuracy."""

        print("Analysing data...")

        # Save each param value range of df_1n to a dictionary
        param_value_1n_min_max_dict=(
            df_merged.groupby("param_key")["param_value_1n"].agg(
                ["min", "max"]).to_dict()
        )

        # Compare param values
        param_value_compare=[]
        total_rows=len(df_merged)
        five_percent_step=total_rows // 20
        progress=0

        for i, (_, row) in enumerate(df_merged.iterrows(), 1):

            # Get row data
            param_key=row["param_key"]
            param_value_1n=row["param_value_1n"]
            param_value_2=row["param_value_2"]

            if isinstance(param_value_1n, str) and isinstance(param_value_2, str):

                comparison=self.compare_strings(param_value_1n, param_value_2)

            elif isinstance(param_value_1n, (float, int)) and isinstance(
                param_value_2, (float, int)
            ):

                # Convert to float if they are numeric
                param_value_1n=float(param_value_1n)
                param_value_2=float(param_value_2)

                # Get parameter value range
                param_value_1n_min=param_value_1n_min_max_dict["min"].get(
                    param_key)
                param_value_1n_max=param_value_1n_min_max_dict["max"].get(
                    param_key)

                if param_value_1n_min is not None and param_value_1n_max is not None:
                    param_value_1n_range=(
                        param_value_1n_min, param_value_1n_max)
                else:
                    param_value_1n_range=None
                    print(f"\nMissing range for: {param_key}")

                # Compare param values
                comparison=self.compare_values(
                    param_value_1n, param_value_2, param_value_1n_range
                )

            else:
                print(f"Param Key: {param_key}, Param Value 1n: "
                      f"{param_value_1n}, Param Value 2: {param_value_2}")
                raise ValueError(
                    f"""Unsupported parameter types for comparison at row {i}:
                    {type(param_value_1n)} and {type(param_value_2)}"""
                )

            # Append to list
            param_value_compare.append(math.floor(comparison))

            # Update loading bar
            if i % five_percent_step == 0 and i != total_rows:
                progress += 5
                print_loading_bar(progress)
            elif i == total_rows:
                progress=100
                print_loading_bar(progress)
                sys.stdout.write("\r\033[K\r")
                sys.stdout.flush()
                print("Analysis complete")

        # Add comparison results to DataFrame
        df_merged["param_value_compare"]=param_value_compare

        # Aggregate analyses
        param_key_list=[]
        param_value_accuracy_mean_list=[]
        param_value_accuracy_min_list=[]
        param_value_accuracy_max_list=[]
        param_value_2_mean_list=[]
        param_value_1n_mean_list=[]
        param_value_mean_accuracy_list=[]
        param_value_2_stan_dev_list=[]
        param_value_1n_stan_dev_list=[]
        stan_dev_accuracy_list=[]

        for param_key, param_data in df_merged.groupby("param_key"):

            # Param value accuracy
            param_value_accuracy_mean=math.floor(
                param_data["param_value_compare"].mean())
            param_value_accuracy_min=math.floor(
                param_data["param_value_compare"].min())
            param_value_accuracy_max=math.floor(
                param_data["param_value_compare"].max())

            # Mean value accuracy
            param_value_2_mean=param_data["param_value_2"].mean()
            param_value_1n_mean=param_data["param_value_1n"].mean()
            param_value_1n_min=param_value_1n_min_max_dict["min"].get(
                param_key)
            param_value_1n_max=param_value_1n_min_max_dict["max"].get(
                param_key)
            if param_value_1n_min is not None and param_value_1n_max is not None:
                param_value_1n_range=(param_value_1n_min, param_value_1n_max)
            else:
                param_value_1n_range=None
                print("Missing range for:\n", param_key)
            param_value_mean_accuracy=math.floor(
                self.compare_values(param_value_1n_mean,
                                    param_value_2_mean, param_value_1n_range)
            )

            # Standard deviation accuracy
            param_2_stan_dev=param_data["param_value_2"].std(ddof=1)
            param_1_stan_dev=param_data["param_value_1n"].std(ddof=1)
            stan_dev_accuracy=math.floor(
                self.compare_analyses(param_2_stan_dev, param_1_stan_dev)
            )

            # Append lists
            param_key_list.append(param_key)

            param_value_accuracy_mean_list.append(param_value_accuracy_mean)
            param_value_accuracy_min_list.append(param_value_accuracy_min)
            param_value_accuracy_max_list.append(param_value_accuracy_max)

            param_value_2_mean_list.append(param_value_2_mean)
            param_value_1n_mean_list.append(param_value_1n_mean)
            param_value_mean_accuracy_list.append(param_value_mean_accuracy)

            param_value_2_stan_dev_list.append(param_2_stan_dev)
            param_value_1n_stan_dev_list.append(param_1_stan_dev)
            stan_dev_accuracy_list.append(stan_dev_accuracy)

        # Create DataFrame of analyses
        df_analysis=pd.DataFrame(
            {
                "Parameter": param_key_list,
                "Mean of Param Sample Accuracy (%)": param_value_accuracy_mean_list,
                "Min of Param Sample Accuracy (%)": param_value_accuracy_min_list,
                "Max of Param Sample Accuracy (%)": param_value_accuracy_max_list,
                "Mean of Param Values (Dataset 2)": param_value_2_mean_list,
                "Mean of Param Values (Dataset 1n)": param_value_1n_mean_list,
                "Mean of Param Values Accuracy (%)": param_value_mean_accuracy_list,
                "Standard Deviation of Param Values (Dataset 2)": param_value_2_stan_dev_list,
                "Standard Deviation of Param Values (Dataset 1n)": param_value_1n_stan_dev_list,
                "Standard Deviation of Param Values Accuracy (%)": stan_dev_accuracy_list,
            }
        )

        return df_analysis

    # Summarise results
    def summarise_results(self, df_analysis):
        """Summarises the analysis for a summary sheet and terminal statement."""

        # Evaluate key results
        mean_of_mean_of_param_sample_accuracy=math.floor(
            df_analysis["Mean of Param Sample Accuracy (%)"].mean()
        )
        min_of_min_of_param_sample_accuracy=math.floor(
            df_analysis["Min of Param Sample Accuracy (%)"].min()
        )
        max_of_max_of_param_sample_accuracy=math.floor(
            df_analysis["Max of Param Sample Accuracy (%)"].max()
        )
        mean_of_mean_of_param_values_accuracy=math.floor(
            df_analysis["Mean of Param Values Accuracy (%)"].mean()
        )
        mean_of_stan_dev_of_param_values_accuracy=math.floor(
            df_analysis["Standard Deviation of Param Values Accuracy (%)"].mean(
            )
        )

        # Describe pass conditions
        pass_conditions=[
            "80-100% incl.",
            "0-100% incl.",
            "95-100% incl.",
            "90-100% incl.",
            "95-100% incl.",
        ]

        # Create DataFrame of summary results
        df_summary=pd.DataFrame(
            {
                "Mean of Mean of Param Sample Accuracy (%)": [
                    mean_of_mean_of_param_sample_accuracy
                ],
                "Min of Min of Param Sample Accuracy (%)": [min_of_min_of_param_sample_accuracy],
                "Max of Max of Param Sample Accuracy (%)": [max_of_max_of_param_sample_accuracy],
                "Mean of Mean of Param Values Accuracy (%)": [
                    mean_of_mean_of_param_values_accuracy
                ],
                "Mean of Standard Deviation of Param Values Accuracy (%)": [
                    mean_of_stan_dev_of_param_values_accuracy
                ],
            }
        )

        df_summary=df_summary.transpose()
        df_summary.columns=["Result %"]
        df_summary["Pass Condition"]=pass_conditions

        def pass_or_fail(row):
            """Determines pass or fail conditions."""
            condition=row["Pass Condition"]
            result=row["Result %"]
            if condition == "80-100% incl.":
                return "Pass" if 80 <= result <= 100 else "Fail"
            elif condition == "0-100% incl.":
                return "Pass" if 0 <= result <= 100 else "Fail"
            elif condition == "95-100% incl.":
                return "Pass" if 95 <= result <= 100 else "Fail"
            elif condition == "90-100% incl.":
                return "Pass" if 90 <= result <= 100 else "Fail"
            elif condition == "95-100% incl.":
                return "Pass" if 95 <= result <= 100 else "Fail"
            else:
                return ""

        # Apply the function to determine pass or fail
        df_summary["Pass or Fail"]=df_summary.apply(pass_or_fail, axis=1)
        pass_or_fail_values=df_summary["Pass or Fail"].tolist()
        overall_result="Pass" if all(
            value == "Pass" for value in pass_or_fail_values) else "Fail"

        # Table formats
        table_formats=[
            "plain",
            "simple",
            "github",
            "grid",
            "fancy_grid",
            "pipe",
            "orgtbl",
            "jira",
            "presto",
            "pretty",
        ]

        # Create analysis summary table
        table_format=table_formats[8]
        print("\nAnalysis Summary:")
        print(
            tabulate(
                df_summary,
                headers="keys",
                tablefmt=table_format,
                numalign="left",
                stralign="left",
            )
        )
        print(f"\nOverall result = {overall_result}")

        return df_summary, overall_result

    def create_plots(
        self,
        df_analysis,
        df_merged,
        output_dir,
        writer,
        current_datetime,
        include_param,
    ):
        """Creates plots from a random sample of parameters."""

        # Define plot params
        num_params_to_plot=36
        num_plots_per_sheet=12
        figsize=(18, 12)
        sheet_name="Sample Plots"

        # Unique param keys
        param_key=df_analysis["Parameter"].unique()

        # Convert param_key to a list for easier manipulation
        param_key_list=list(param_key)

        # Check if included param exists
        if include_param:
            if include_param not in param_key_list:
                raise ValueError(
                    f"'{include_param}' is not a valid parameter key.")

            # Remove include_param from the sampling pool to avoid duplication
            param_key_list.remove(include_param)

            # Limit the number of parameters to sample to the available size
            sample_size=min(num_params_to_plot - 1, len(param_key_list))

            # Sample param_key_list, excluding include_param
            param_key_subset=random.sample(param_key_list, sample_size)

            # Include the specified parameter at the start of the list
            param_key_subset.insert(0, include_param)
        else:
            # Limit the number of parameters to sample to the available size
            sample_size=min(num_params_to_plot, len(param_key_list))

            # Sample param_key_subset without include_param
            param_key_subset=random.sample(param_key_list, sample_size)

        # Calculate number of sheets needed
        num_sheets=math.ceil(len(param_key_subset) / num_plots_per_sheet)

        # Plots samples
        start_idx=0
        for i in range(num_sheets):

            end_idx=min(start_idx + num_plots_per_sheet, len(param_key_subset))
            param_key_sheet=param_key_subset[start_idx:end_idx]

            fig, axs=plt.subplots(3, 4, figsize=figsize)
            fig.suptitle(f"{sheet_name} {i + 1}")

            for j, param_key in enumerate(param_key_sheet):

                ax=axs[j // 4, j % 4]

                # Filter data for the current parameter
                param_data_merged=df_merged[df_merged["param_key"]
                    == param_key]

                # Convert time delta to seconds
                param_data_merged.loc[:, "time_delta_2"] /= 1e9
                param_data_merged.loc[:, "time_delta_1n"] /= 1e9

                # Check if the parameter is Boolean
                is_boolean=param_data_merged["param_value_2"].isin(
                    [0.0, 1.0]).all()

                # Plot data (can be customized for boolean or float)
                if is_boolean:
                    sns.lineplot(
                        x="time_delta_2",
                        y="param_value_2",
                        data=param_data_merged,
                        ax=ax,
                        label="Dataset 2",
                        color="blue",
                        linestyle="-",
                        linewidth=0.5,
                        drawstyle="steps-post",
                    )

                    sns.lineplot(
                        x="time_delta_1n",
                        y="param_value_1n",
                        data=param_data_merged,
                        ax=ax,
                        label="Dataset 1",
                        color="red",
                        linestyle="-",
                        linewidth=0.5,
                        drawstyle="steps-post",
                    )

                else:
                    sns.lineplot(
                        x="time_delta_2",
                        y="param_value_2",
                        data=param_data_merged,
                        ax=ax,
                        label="Dataset 2",
                        color="blue",
                        linestyle="-",
                        linewidth=0.5,
                        drawstyle="steps-post",
                    )

                    sns.lineplot(
                        x="time_delta_1n",
                        y="param_value_1n",
                        data=param_data_merged,
                        ax=ax,
                        label="Dataset 1",
                        color="red",
                        linestyle="-",
                        linewidth=0.5,
                        drawstyle="steps-post",
                    )

                # Set chart detail
                ax.set_title(param_key)
                ax.legend()
                ax.set_xlabel("Time Delta (s)")
                ax.set_ylabel("Param Value")

                if j == len(param_key_sheet) - 1:
                    for k in range(j + 1, num_plots_per_sheet):
                        axs[k // 4, k % 4].axis("off")

            plt.tight_layout(rect=[0, 0.03, 1, 0.95])

            # Ensure the plots directory exists in the root folder
            os.makedirs(f"{output_dir}/plots", exist_ok=True)

            # Save the figure as PNG in the plots directory
            plot_filename=f"{output_dir}/plots/plot_{i}_{current_datetime}.png"
            plt.savefig(plot_filename)

            # Insert the plot into the Excel file
            sheet_name_with_suffix=f"{sheet_name} {i + 1}" if num_sheets > 1 else sheet_name

            # Add plot to worksheet
            worksheet=writer.book.add_worksheet(sheet_name_with_suffix)
            writer.sheets[sheet_name_with_suffix]=worksheet
            worksheet.insert_image("A1", plot_filename)
            start_idx=end_idx

    def create_directories(self, input_file_1, input_file_2):
        """Creates directories for input and output data."""

        # Capture datetime for output file creation
        current_datetime=datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

        # Create output directory
        output_dir=f"output_dataset_compare/{current_datetime}"
        os.makedirs(output_dir, exist_ok=True)

        # Create output file name
        output_file_name=f"{output_dir}/output_dataset_compare_{current_datetime}.xlsx"

        # Create input directory
        input_data_dir=os.path.join(output_dir, "input_data")
        os.makedirs(input_data_dir, exist_ok=True)

        # Copy input files to input directory
        shutil.copy(input_file_1, input_data_dir)
        shutil.copy(input_file_2, input_data_dir)

        # Create writer
        writer=pd.ExcelWriter(output_file_name, engine="xlsxwriter")

        return current_datetime, output_dir, output_file_name, writer

    def split_dataframe(self, df, chunk_size):

        chunks=[df.iloc[i: i + chunk_size]
            for i in range(0, len(df), chunk_size)]

        return chunks

    def format_excel_sheet(self, writer, sheet, end_column):

        left_align_format=writer.book.add_format({"align": "left"})
        sheet.set_column(f"A:{end_column}", None, left_align_format)
        sheet.autofit()
        sheet.autofilter(f"A1:{end_column}1")

    def write_data_to_excel(self, writer, dataframe, sheet_name_prefix, formatting_letter):
        """Writes sheets to Excel."""

        max_rows_per_sheet=1048576

        if len(dataframe) > max_rows_per_sheet:
            chunks=self.split_dataframe(dataframe, max_rows_per_sheet)
            for i, chunk in enumerate(chunks):
                sheet_name=f"{sheet_name_prefix} Part {i + 1}"
                chunk.to_excel(
                    writer,
                    sheet_name=sheet_name,
                    index=False,
                    header=True,
                    freeze_panes=(1, 0),
                )
                self.format_excel_sheet(
                    writer, writer.sheets[sheet_name], formatting_letter)
        else:
            dataframe.to_excel(
                writer,
                sheet_name=sheet_name_prefix,
                index=False,
                header=True,
                freeze_panes=(1, 0),
            )
            self.format_excel_sheet(
                writer, writer.sheets[sheet_name_prefix], formatting_letter)

    def write_to_excel(
        self,
        df_summary,
        df_analysis,
        df_merged,
        include_param,
        overall_result,
        input_file_1,
        input_file_2,
        switch,
        missing_keys_1,
        missing_keys_2,
        df_type_diff,
    ):
        """Writes full analysis to Excel."""

        print("\nCreating output file...")

        # Get directories
        current_datetime, output_dir, output_file_name, writer=self.create_directories(
            input_file_1, input_file_2
        )

        # Convert timestamps greater than 15 digits (Excel limit) to string
        df_merged["timestamp_2"]=df_merged["timestamp_2"].astype(str)
        df_merged["timestamp_1n"]=df_merged["timestamp_1n"].astype(str)

        # Create a dictionary of summary data
        summary_data={
            (7, 0): "Overall Pass or Fail:",
            (7, 1): overall_result,
            (9, 0): "Input File 1:",
            (9, 1): input_file_1,
            (10, 0): "Input File 2:",
            (10, 1): input_file_2,
            (11, 0): "Files Switched:",
            (11, 1): switch,
            (12, 0): "Script Run Time",
            (14, 0): "Missing Parameters",
            (14, 3): "Inconsistent Param Value Types",
            (15, 0): "Missing in File 1",
            (15, 1): "Missing in File 2",
        }

        # Write the dictionary to the summary sheet
        print("Creating sheet, 'Analysis Summary'...")
        df_summary.to_excel(writer, sheet_name="Analysis Summary", index=True)

        # Add dictionary items
        summary_sheet=writer.sheets["Analysis Summary"]
        for (row, col), value in summary_data.items():
            summary_sheet.write(row, col, value)

        # Add missing keys, if any
        if not missing_keys_1:
            summary_sheet.write(16, 0, "None")
        else:
            for idx, key in enumerate(missing_keys_1):
                summary_sheet.write(16 + idx, 0, key)
        if not missing_keys_2:
            summary_sheet.write(16, 1, "None")
        else:
            for idx, key in enumerate(missing_keys_2):
                summary_sheet.write(16 + idx, 1, key)

        # Write data type differences from df_merged
        if df_type_diff.empty:
            summary_sheet.write(15, 3, "None")
        else:
            df_type_diff.to_excel(
                summary_sheet,
                startrow=15,
                startcol=3,
                index=False,
                header=["Parameter Name", "Type 2", "Type 1n"],
            )

        # Write other dataframes to workbook
        print("Creating sheet, 'Merged Data'...")
        self.write_data_to_excel(writer, df_merged, "Merged Data", "L")
        print("Creating sheet, 'Parameter Analysis'...")
        self.write_data_to_excel(
            writer, df_analysis, "Parameter Analysis", "J")

        # Create plots
        print("Creating sample plots...")
        self.create_plots(
            df_analysis, df_merged, output_dir, writer, current_datetime, include_param
        )

        # Calculate time taken and add to summary sheet
        time_taken=math.floor(time.time() - self.start_time)
        summary_sheet.write(12, 1, time_taken)
        summary_sheet.set_column(
            "A:D", None, writer.book.add_format({"align": "left"}))
        summary_sheet.autofit()

        # Close the writer
        writer.close()

        # Print completion message
        print("Output file complete")
        print(f"Output file = {output_file_name}")
        print(f"Script run time = {time_taken} seconds")
        print("\n")

    def main(self, args):

        # Store input arguments
        input_file_1=args.input_file_1
        input_file_2=args.input_file_2
        time_adjust_1=args.shift_1
        time_adjust_2=args.shift_2
        if args.include_param:
            include_param=args.include_param
        else:
            include_param=None

        # Load datasets
        df_1, df_2=self.load_datasets(
            input_file_1, input_file_2, time_adjust_1, time_adjust_2)

        # Check order
        df_1, df_2, mean_delta_1_interval, mean_delta_2_interval, switch=self.check_order(
            df_1, df_2
        )

        # Remove prefixes
        df_1, df_2, removed_info=self.remove_prefixes(df_1, df_2)

        # Check params
        (
            df_1,
            df_2,
            missing_keys_1,
            missing_keys_2,
            param_key_1_nans,
            param_key_2_nans,
            non_convertible_keys,
        )=self.check_params(df_1, df_2)

        # Load summary
        self.load_summary(
            mean_delta_1_interval,
            mean_delta_2_interval,
            input_file_1,
            input_file_2,
            switch,
            removed_info,
            param_key_1_nans,
            param_key_2_nans,
            missing_keys_1,
            missing_keys_2,
            non_convertible_keys,
        )

        # Merge datasets
        df_merged, df_type_diff=self.merge_datasets(df_1, df_2)

        # Analyse data
        df_analysis=self.analyse_data(df_merged)

        # Summarise results
        df_summary, overall_result=self.summarise_results(df_analysis)

        # Write merged dataset, analysis, and results to Excel
        self.write_to_excel(
            df_summary,
            df_analysis,
            df_merged,
            include_param,
            overall_result,
            input_file_1,
            input_file_2,
            switch,
            missing_keys_1,
            missing_keys_2,
            df_type_diff,
        )


def run():
    parser=argparse.ArgumentParser(
        description="""Compares the accuracy
                                     of two datasets."""
    )
    parser.add_argument(
        "input_file_1",
        type=str,
        help="""Input file 1 in .csv or parquet
                          format: time, param, value. Can handle header or no header.""",
    )
    parser.add_argument(
        "input_file_2",
        type=str,
        help="""Input file 2 in .csv or parquet
                          format: time, param, value. Can handle header or no header.""",
    )
    parser.add_argument(
        "--shift_1", "-s1",
        type=float,
        default=0,
        help="""Input file 1 time adjustment in seconds
                          (e.g., to align samples using 0.2s offset).
                            Default=0""",
    )
    parser.add_argument(
        "--shift_2", "-s2",
        type=float,
        default=0,
        help="""Input file 2 time adjustment in seconds
                          (e.g., to align samples using 0.2s offset).
                            Default=0""",
    )
    parser.add_argument(
        "--include_param", "-i",
        type=str,
        default=None,
        help="""Parameter to include in sample plots.""",
    )
    parser.add_argument(
        "--debug", "-d",
        action='store_true',
        help="""Enable debug statements.""",
    )

    args=parser.parse_args()

    # Create logger instance with debug enabled if the flag is set
    logger_instance=CustomLogger(enabled=args.debug)

    # Check files exist
    if not os.path.exists(args.input_file_1):
        print(f"File {args.input_file_1} does not exist.")
        return
    if not os.path.exists(args.input_file_2):
        print(f"File {args.input_file_2} does not exist.")
        return

    # Instantiate the DatasetCompare with the logger
    dataset_compare=DatasetCompare(logger=logger_instance)

    # Call main method
    dataset_compare.main(args)


if __name__ == "__main__":
    run()



python.exe - m pip install - -upgrade pip
python - m venv .venv
deactivate
.venv\Scripts\activate
.venv\Scripts\Activate.ps1        
pip freeze > requirements.txt
pip install -r requirements.txt
autopep8 -h
autopep8 backend/document_query_app.py -i --max-line-length 79
black backend/document_query_app.py     
uvicorn api:app --reload 
pip install fastapi uvicorn
ollama run gemma2:9b
pip install pdfplumber pymupdf 
pip install yfinance     
pip list
pip install fastparquet

import influxdb_client_3 as InfluxDBClient3
from influxdb_client_3 import flight_client_options
import certifi
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import islice
import sys
import os
import time
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import query_tools
import pandas as pd
from collections import OrderedDict
from pandasql import sqldf
from typing import Listimport pandas as pd
import datetime
import math
import random
import matplotlib.pyplot as plt
import seaborn as sns
import os
import time
import argparse
import shutil
import sys
from tabulate import tabulate
from pandas.io.formats import excel
from os.path import basename


A JSONL file doesn’t inherently have a different file extension from a standard JSON file based on any strict specification—it’s more of a convention. Both JSON and JSONL files can technically use the .json extension, but to distinguish JSONL files (which use the "JSON Lines" format), people often use the .jsonl extension. This is purely a naming convention to make it clear that the file follows the JSONL structure (one JSON object per line) rather than standard JSON (a single JSON object or array).

Common Extensions
.json: Typically used for standard JSON files (e.g., a single object or array).
.jsonl: Commonly used for JSON Lines files to indicate the line-by-line format.
Other variations like .ndjson (Newline Delimited JSON) or .jl (JSON Lines) are also used occasionally, though .jsonl is the most widely recognized.
Why the Distinction Matters
While the extension doesn’t change how the file is processed (it’s still just text), using .jsonl helps developers and tools quickly identify the file’s format. For example:

A tool or library might expect .json to be a single JSON structure and fail on a JSONL file unless explicitly told to handle it line-by-line (e.g., with lines=True in Pandas).
.jsonl signals that each line should be parsed independently.
Examples
File: data.json (Standard JSON)
text
Wrap
Copy
[{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
Extension: .json
Parsed with: pd.read_json('data.json') (no lines=True needed)
File: data.jsonl (JSON Lines)
text
Wrap
Copy
{"name": "Alice", "age": 25}
{"name": "Bob", "age": 30}
Extension: .jsonl (though it could still be .json)
Parsed with: pd.read_json('data.jsonl', lines=True)
In Practice
You can name a JSONL file data.json and it’ll work fine as long as your parsing tool knows it’s JSONL (e.g., via lines=True).
However, using .jsonl is a helpful convention to avoid confusion, especially in projects where both formats might coexist.
So, while JSONL doesn’t require a different extension, .jsonl has become the de facto standard to differentiate it from traditional JSON files.


import json

with open('data.jsonl', 'r') as file:
    for line in file:
        data = json.loads(line.strip())  # strip() removes trailing newlines
        print(data['name'], data['age'])

import json

# For a standard JSON file (not JSONL)
with open('data.json', 'r') as file:
    data = json.load(file)  # Reads entire file as one JSON object



are .ndjson and .jl just other names for .jsonl or is it a differnet format? What other formats should I be aware of?


The extensions .ndjson (Newline Delimited JSON) and .jl (JSON Lines) are indeed just alternative names for the same format as .jsonl. They all refer to the JSON Lines format, where each line in the file is a standalone, valid JSON object, separated by newlines. There’s no structural difference between .jsonl, .ndjson, and .jl—they’re synonymous in terms of content and purpose. The variation in naming comes from different communities or tools adopting their preferred terminology.

Confirmation: Same Format
.jsonl: Most common and widely recognized (popularized by the JSON Lines specification at jsonlines.org).
.ndjson: Stands for "Newline Delimited JSON," often used in contexts like data streaming or logging (see ndjson.org).
.jl: A shorter, less common alias for JSON Lines.
All three extensions represent this format:

text
Wrap
Copy
{"name": "Alice", "age": 25}
{"name": "Bob", "age": 30}
{"name": "Charlie", "age": 35}
You’d parse any of these files the same way in Python, e.g., with pandas.read_json('file.ndjson', lines=True) or a line-by-line reader like json.loads() in a loop.

Why Multiple Names?
The different extensions reflect historical or contextual preferences:

JSON Lines (.jsonl): Emphasizes the line-based structure.
NDJSON (.ndjson): Highlights the newline delimiter, often tied to streaming or real-time data use cases.
JL (.jl): A concise shorthand, though less common.
Despite the naming differences, there’s no functional distinction—they’re interchangeable.

Other Related Formats to Be Aware Of
While .jsonl, .ndjson, and .jl are the same, there are other data formats you might encounter that are related or serve similar purposes. Here are some worth knowing:

Standard JSON (.json)
A single JSON object or array, not line-based.
Example:
text
Wrap
Copy
[{"name": "Alice"}, {"name": "Bob"}]
Doesn’t require lines=True for parsing.
CSV (.csv)
Comma-separated values, a tabular format, not JSON-based but often used for similar purposes (e.g., row-by-row data).
Example:
text
Wrap
Copy
name,age
Alice,25
Bob,30
Parsed with pandas.read_csv().
Parquet (.parquet)
A columnar storage format, optimized for big data processing (e.g., with Apache Spark or Pandas).
Not human-readable like JSONL, but often used as a more efficient alternative for large datasets.
Parsed with pandas.read_parquet().
Avro (.avro)
A binary serialization format with a JSON-like schema, used in data streaming (e.g., Apache Kafka).
Not line-based like JSONL, but schema-driven and compact.
TSV (.tsv)
Tab-separated values, similar to CSV but using tabs instead of commas.
Example:
text
Wrap
Copy
name    age
Alice   25
Bob     30
Parsed with pandas.read_csv(..., sep='\t').
Line-Delimited Formats (Generic)
Some tools use custom line-delimited formats that aren’t strictly JSONL but follow a similar idea (e.g., log files with one entry per line in a non-JSON structure).
Key Differences from JSONL
Structure: JSONL is specifically JSON objects, one per line. Formats like CSV or TSV are tabular and not JSON-based.
Use Case: JSONL is great for streaming, appending, or semi-structured data. Parquet/Avro are better for performance with large datasets.
Readability: JSONL, CSV, and TSV are human-readable; Parquet and Avro are binary and not easily readable without tools.
When to Use JSONL (or .ndjson, .jl)?
When you need a simple, appendable, human-readable format.
Common in logging, data pipelines, or datasets too large for a single JSON array.
Summary
.ndjson and .jl are the same as .jsonl: Just different names for the JSON Lines format.
Other formats to know: Standard JSON (.json), CSV (.csv), Parquet (.parquet), Avro (.avro), TSV (.tsv), etc., each with distinct use cases and parsing methods.
If you’re working with line-delimited JSON, any of .jsonl, .ndjson, or .jl will do—just pick one your team or tools recognize! Let me know if you want deeper details on any of these formats.




import pandas as pd
import fastparquet as fp
from typing import Optional


class LapTimeProcessor:
    """
    A class to process lap time data and driver details, merge them,
    and save the results to a partitioned Parquet file.

    Attributes:
        df_bahrain (pd.DataFrame): DataFrame containing Bahrain lap time data.
        df_drivers (pd.DataFrame): DataFrame containing driver details.
        df_merge (pd.DataFrame): DataFrame resulting from merging df_bahrain and df_drivers.
    """

    def __init__(self):
        self.df_bahrain: Optional[pd.DataFrame] = None
        self.df_drivers: Optional[pd.DataFrame] = None
        self.df_merge: Optional[pd.DataFrame] = None

    def load_data(self, lap_times_csv: str, drivers_json: str) -> None:
        """
        Load lap time data from a CSV file and driver details from a JSON file.

        Args:
            lap_times_csv (str): Path to the CSV file containing Bahrain lap times.
            drivers_json (str): Path to the JSON file containing driver details.
        """
        self.df_bahrain = pd.read_csv(lap_times_csv)
        self.df_drivers = pd.read_json(drivers_json, lines=True)
        self.df_bahrain = self.df_bahrain.dropna(subset=["Laptimes"])

    def merge_data(self) -> None:
        """
        Merge the Bahrain lap times DataFrame with the driver details DataFrame.
        """
        self.df_merge = pd.merge(
            self.df_bahrain,
            self.df_drivers,
            left_on="DriverNumber",
            right_on="driver_name",
            how="left",
        )
        self.df_merge["Laptimes"] = pd.to_timedelta(self.df_merge["Laptimes"])

    def sort_data(self) -> pd.DataFrame:
        """
        Sort the merged DataFrame by lap times.

        Returns:
            pd.DataFrame: The sorted DataFrame.
        """
        sorted_df = self.df_merge.sort_values(by="Laptimes")
        return sorted_df

    def find_fastest_laps(self) -> pd.DataFrame:
        """
        Find the fastest lap times for each driver.

        Returns:
            pd.DataFrame: DataFrame with the fastest lap times per driver.
        """
        fastest_laps = self.df_merge.groupby("DriverNumber", as_index=False).agg(
            {"Laptimes": "min"}
        )
        return fastest_laps

    def save_to_parquet(self, output_dir: str) -> None:
        """
        Save the merged DataFrame to a partitioned Parquet file.

        Args:
            output_dir (str): Directory to save the partitioned Parquet files.
        """
        fp.write(output_dir, self.df_merge, partition_on=["DriverNumber", "Compound"])

    def read_parquet(self, input_dir: str) -> pd.DataFrame:
        """
        Read a partitioned Parquet file into a DataFrame.

        Args:
            input_dir (str): Directory containing the partitioned Parquet files.

        Returns:
            pd.DataFrame: DataFrame read from the partitioned Parquet files.
        """
        return fp.ParquetFile(input_dir).to_pandas()


# Example usage
if __name__ == "__main__":
    processor = LapTimeProcessor()
    processor.load_data("bahrain_laptimes.csv", "driver_details.json")
    processor.merge_data()

    print("Merged DataFrame:")
    print(processor.df_merge)

    sorted_df = processor.sort_data()
    print("\nSorted DataFrame by Laptimes:")
    print(sorted_df)

    fastest_laps = processor.find_fastest_laps()
    print("\nFastest lap times per driver:")
    print(fastest_laps)

    processor.save_to_parquet("partitioned_laptimes.parquet")

    df_read_back = processor.read_parquet("partitioned_laptimes.parquet")
    print("\nDataFrame read back from partitioned Parquet file:")
    print(df_read_back)



    import requests
import pandas as pd
import json

def fetch_json_to_dataframe(api_url):
    try:
        # Step 1: Make the API request
        response = requests.get(api_url)
        
        # Check if the request was successful (status code 200)
        response.raise_for_status()
        
        # Step 2: Parse the JSON response
        json_data = response.json()  # Automatically parses JSON into Python object
        
        # Step 3: Convert JSON to Pandas DataFrame
        # If the JSON is a list of objects, this works directly
        df = pd.DataFrame(json_data)
        
        # Step 4: Print the DataFrame
        print("DataFrame from API:")
        print(df)
        
        return df  # Return the DataFrame for further use if needed
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None
    except ValueError as e:
        print(f"Error parsing JSON: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Example usage with JSONPlaceholder API (fake posts data)
api_url = "https://jsonplaceholder.typicode.com/posts"
dataframe = fetch_json_to_dataframe(api_url)

# Optional: If you want to inspect the first few rows
if dataframe is not None:
    print("\nFirst 5 rows:")
    print(dataframe.head())