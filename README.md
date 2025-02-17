# I-ALiRT Data Access Package

This lightweight Python package allows users to query and download log data.

## Command Line Utility

### To install

```bash
pip install ialirt-data-access
ialirt-data-access -h
```

### Query / Search for logs

Find all files from a given year, day of year, and instance

```bash
$ ialirt-data-access --url <url> ialirt-log-query --year <year> --doy <doy> --instance <instance>
```

### Download logs

Download a log and place in Downloads directory or optionally specify another local directory by appending --downloads_dir <directory> to the command

```bash
$ ialirt-data-access --url <url> ialirt-log-download --filename <filename>
```

### Query the database

Query the database for a given time and/or data product. Examples shown below.

```bash
$ ialirt-data-access --url <url> ialirt-db-query --insert_time_start <insert_time_start> --insert_time_end <insert_time_end> --product_name <product_name>
```
or
```bash
$ ialirt-data-access --url <url> ialirt-db-query --met_start <met_start> --met_end <met_end>
```
or
```bash
$ ialirt-data-access --url <url> ialirt-db-query --product_name <product_name>
```
or
```bash
$ ialirt-data-access --url <url> ialirt-db-query --met_start <met_start> --product_name <product_name_prefix*>
```


## Importing as a package

```python
import ialirt_data_access

# Search for files
results = ialirt_data_access.query(year="2024", doy="045", instance="1")
```

## Configuration

### Data Access URL

To change the default URL that the package accesses, you can set
the environment variable ``IALIRT_DATA_ACCESS_URL`` or within the
package ``ialirt_data_access.config["DATA_ACCESS_URL"]``. The default
is the development server ``https://ialirt.dev.imap-mission.com``.

## Troubleshooting

### Network issues

#### SSL

If you encounter SSL errors similar to the following:

```text
urllib.error.URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:997)>
```

That generally means the Python environment you're using is not finding your system's root
certificates properly. This means you need to tell Python how to find those certificates
with the following potential solutions.

1. **Upgrade the certifi package**

    ```bash
    pip install --upgrade certifi
    ```

2. **Install system certificates**
    Depending on the Python version you installed the program with the command will look something like this:

    ```bash
    /Applications/Python\ 3.10/Install\ Certificates.command
    ```

#### HTTP Error 502: Bad Gateway

This could mean that the service is temporarily down. If you
continue to encounter this, reach out to the IMAP SDC at
<imap-sdc@lasp.colorado.edu>.
