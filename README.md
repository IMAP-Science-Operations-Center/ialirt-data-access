# I-ALiRT Data Access Package

This lightweight Python package allows users to query the I-ALiRT database and list/download files from S3.

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

### Query / Search for packets

Find all files from a given year, day of year, hour, minute, and second.

```bash
$ ialirt-data-access --url <url> ialirt-packet-query --year <year> --doy <doy> [--hh <hour>] [--mm <minute>] [--ss <second>]
```

### Download from S3

Download a file and place it in the Downloads/<filetype> directory by default, or optionally specify another location using --downloads_dir. Valid filetype options include: logs, packets, archive.

```bash
$ ialirt-data-access --url <url> ialirt-download --filetype <filetype> --filename <filename>
```

### Query the database

Query the database for a given time. Examples shown below.
Valid --instrument values include:

- hit
- mag
- codice_lo
- codice_hi
- swapi
- swe
- spice               (metadata about kernels)
- spacecraft          (IMAP ephemeris state vectors)
- <instrument>_hk     (housekeeping telemetry)

If omitted, the query returns science instruments for the selected time range.

```bash
$ ialirt-data-access --url <url> space-weather --met_in_utc_start <met_in_utc_start> --met_in_utc_end <met_in_utc_end>
```
or to query 1 hr from a start time
```bash
$ ialirt-data-access --url <url> space-weather --time_utc_start <time_utc_start>
```
or to query the past 1 hr from an end time
```bash
$ ialirt-data-access --url <url> space-weather --time_utc_end <time_utc_end>
```
or to query a specific instrument within the past hour
```bash
$ ialirt-data-access --url <url> space-weather --instrument <instrument>
```
or to query spice metadata
```bash
$ ialirt-data-access --url <url> space-weather --instrument spice
```
or to query housekeeping for a specific instrument
```bash
$ ialirt-data-access --url <url> space-weather --instrument <instrument>_hk
```
or to query imap spacecraft position and velocity
```bash
$ ialirt-data-access --url <url> space-weather --instrument spacecraft
```
an equivalent curl command would be
```bash
$ curl "https://ialirt.imap-mission.com/space-weather?instrument=mag&time_utc_start=2025-11-22T05:30:00&time_utc_end=2025-11-22T08:30:00"
```

## Importing as a package

```python
import ialirt_data_access

# Search for files
results = ialirt_data_access.log_query(year="2024", doy="045", instance="1")
```

## Configuration

### Data Access URL

To change the default URL that the package accesses, you can set
the environment variable ``IALIRT_DATA_ACCESS_URL`` or within the
package ``ialirt_data_access.config["DATA_ACCESS_URL"]``. The default
is the production server ``https://ialirt.imap-mission.com``.


### Automated use with API Keys

The default for the CLI is to use the public endpoints.
To access some unreleased data products and quicklooks, you may
need elevated permissions. To programmatically get that, you need
an API Key, which can be requested from the SDC team.

To use the API Key you can set environment variables and then use
the tool as usual. Note that the api endpoints are prefixed with `/api-key`
to request unreleased data. This will also require an update to the
data access url. So the following should be used when programatically
accessing the data.

```bash
IMAP_API_KEY=<your-api-key> IALIRT_DATA_ACCESS_URL=https://ialirt.imap-mission.com/api-key ialirt-data-access ...
```

or with CLI flags

```bash
ialirt-data-access --api-key <your-api-key> --url https://ialirt.imap-mission.com/api-key ...
```

Example:
```bash
ialirt-data-access --api-key <api_key> --url https://ialirt.imap-mission.com/api-key space-weather --instrument <instrument>
```
An equivalent curl command would be:
```bash
$ curl -H "x-api-key: $IALIRT_API_KEY" "https://ialirt.imap-mission.com/api-key/space-weather?instrument=mag"
```

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
