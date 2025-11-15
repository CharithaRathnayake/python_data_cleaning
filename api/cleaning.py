import pandas as pd
import re

# Load CSV (update the path)
df = pd.read_csv("./api/stock_market.csv")

# Shape (rows, columns)
print("Shape:", df.shape)

# Preview first 5 rows
print("\nHead:")
print(df.head())

# Info (schema, dtypes, nulls)
print("\nSchema / Info:")
print(df.info())

# Null summary
print("\nNull Summary:")
print(df.isnull().sum())

# print(df.columns)

# Function to convert column names to snake_case
def to_snake(name: str) -> str:
    # lower cases
    name = name.lower() 
    # split by spaces
    names = name.split(" ")
    # trim the spaces and join with underscores
    name = "_".join([n.strip() for n in names])
    return name

df.columns = [to_snake(c) for c in df.columns]

# Standardize string columns: trim spaces and convert to lowercase
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

str_cols = df.select_dtypes(include="object").columns

df[str_cols] = df[str_cols].apply(lambda col: col.str.lower())
# Preview cleaned DataFrame
print("\nCleaned DataFrame Head:")
print(df.head())

# Identify and standardize missing value markers
missing_markers = ["", "na", "n/a", "null", "-","nan","NA","N/A","NULL","NaN"]
df.replace(missing_markers, pd.NA, inplace=True)
df = df.where(df.notna(), pd.NA)

# Final null summary
print("\nFinal Null Summary:")
print(df.head())

# Define target schema
target_schema = {
    "trade_date": "date",
    "ticker": "string",
    "open_price": "float",
    "close_price": "float",
    "volume": "int",
    "sector": "string",
    "validated": "bool",
    "currency": "string",
    "exchange": "string",
    "notes": "string"
}

# parse dates, cast types
for col, kind in target_schema.items():
    if col not in df.columns:
        continue

    if kind == "date":
        df["col"] = pd.to_datetime(df["trade_date"], format="%Y/%m/%d", errors="coerce")
    elif kind == "string":
        df[col] = df[col].astype("string")
    elif kind == "int":
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    elif kind == "float":
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Float64")
    elif kind == "bool":
        df[col] = (
            df[col]
            .astype("string")
            .str.strip()
            .str.lower()
            .map(
                {
                    "true": True, "t": True, "yes": True, "y": True, "1": True,
                    "false": False, "f": False, "no": False, "n": False, "0": False,
                }
            )
            .astype("boolean")
        )

print("\nDataFrame Info After Type Casting:")
print(df.head())
# 3) Deduplicate rows
before = len(df)
df = df.drop_duplicates()
after = len(df)
print(f"\nDeduplicated rows: {before - after} removed, {after} remaining.")

# 4) Save to Parquet
output_path = "./api/cleaned.parquet"
df.to_parquet(output_path, index=False, engine="pyarrow")
print(f"Saved cleaned data to: {output_path}")