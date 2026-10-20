# Welcome to I-ALiRT Data Access!

This page provides lightweight Python tools to allow users to query and access I-ALiRT data.

It also serves as a central location for I-ALiRT data feature requests or bug reports, through the "Issues" pages.

The I-ALiRT team welcomes any and all discussions or contributions! If you have any questions, comments, requests, or anything else, please do open an issue. If you have thoughts on an existing issue or pull request, we welcome comments and discussion everywhere.

If you are interested in contributing to the project, welcome! Please start here.

## Contacting the I-ALiRT Team

### Asking questions

If you have any questions about using I-ALiRT that are not covered by the existing documentation, you can open a [question-type Issue](https://github.com/IMAP-Science-Operations-Center/ialirt-data-access/issues/new/choose). Before you open a new issue, please search through the existing answered questions and documentation to see if your question has already been answered.

### Feature requests

For new feature requests, you can open a "feature request" ticket for I-ALiRT. Please fill out with as much detail as you can. Please also do a search through existing tickets to see if an existing ticket already

This lightweight Python package allows users to query the I-ALiRT database and list/download files from S3.

### Contributions

The I-ALiRT project welcomes contributions! To contribute, please consult the IMAP [Contribution guide](https://imap-processing.readthedocs.io/en/latest/development/index.html). All IMAP repositories follow these standards.

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

Two mutually exclusive query modes are supported.

**Individual params mode** — query by partial datetime (year and doy required):

```bash
$ ialirt-data-access --url <url> ialirt-packet-query --year <year> --doy <doy> [--hh <hour>] [--mm <minute>] [--ss <second>]
```

**UTC range mode** — query by ISO 8601 time range (time_utc_start required):

```bash
$ ialirt-data-access --url <url> ialirt-packet-query --time_utc_start <YYYY-MM-DDTHH:MM:SS> [--time_utc_end <YYYY-MM-DDTHH:MM:SS>]
```

### Query / Search for archive CDF files

Find all archive CDF files, optionally filtered by year, month, and day. All parameters are optional; version defaults to 1.

```bash
$ ialirt-data-access --url <url> ialirt-archive-query [--year <year>] [--month <month>] [--day <day>] [--version <version>]
```

Or use `--since` to get all files on or after a given date (format: YYYYMMDD). Cannot be combined with `--year`, `--month`, or `--day`.

```bash
$ ialirt-data-access --url <url> ialirt-archive-query --since <yyyymmdd> [--version <version>]
```

An equivalent curl command is shown.

```bash
$ curl "https://ialirt.imap-mission.com/ialirt-archive-query?year=2024&month=05&day=21&version=1"
```

```bash
$ curl "https://ialirt.imap-mission.com/ialirt-archive-query?since=20240521&version=1"
```

### Download from S3

Download a file and place it in the Downloads/<filetype> directory by default, or optionally specify another location using --downloads_dir. Valid filetype options include: logs, packets, archive.

```bash
$ ialirt-data-access --url <url> ialirt-download --filetype <filetype> --filename <filename>
```

An example of how to download a cdf file from the archive directory is shown.

```bash
$ ialirt-data-access --url https://ialirt.imap-mission.com ialirt-download --filetype archive --filename imap_ialirt_l1_realtime_<yyyymmdd>_v<NNN>.cdf
```

An equivalent curl command is shown.

```bash
$ curl -L -O "https://ialirt.imap-mission.com/ialirt-download/archive/imap_ialirt_l1_realtime_<yyyymmdd>_v<NNN>.cdf"
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
- spice (metadata about kernels)
- spacecraft (IMAP ephemeris state vectors)
- <instrument>\_hk (housekeeping telemetry)

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

### Query the SSR database

SSR data products are processed from the full day of I-ALiRT packets,
about a week after the data was taken. The query works like
`space-weather`, with an optional `--version` (default `v001`).
Valid --instrument values include:

- hit
- mag
- codice_lo
- codice_hi
- swapi
- swe
- spacecraft (IMAP ephemeris state vectors)
- spacecraft_status (requires an API key)
- mag_hk (MAG housekeeping, requires a full scope API key)
- spice (SPICE kernels used)
- ancillary (ancillary files used)

If omitted, the query returns science instruments. If no time range is
given, the latest 1 hour of data for each instrument is returned.

```bash
$ ialirt-data-access --url <url> space-weather-ssr --instrument mag --time_utc_start <time_utc_start> --time_utc_end <time_utc_end>
```

or to query a specific version

```bash
$ ialirt-data-access --url <url> space-weather-ssr --instrument mag --version v002 --time_utc_start <time_utc_start>
```

Each data product has a `kernel_set_key`. To see the SPICE kernels or
ancillary files used to make it, query `spice` or `ancillary` with the
same version and both times set to that `kernel_set_key`:

```bash
$ ialirt-data-access --url <url> space-weather-ssr --instrument spice --time_utc_start <kernel_set_key> --time_utc_end <kernel_set_key>
```

an equivalent curl command would be

```bash
$ curl "https://ialirt.imap-mission.com/space-weather-ssr?instrument=mag&version=v001&time_utc_start=2026-09-01T05:30:00&time_utc_end=2026-09-01T06:30:00"
```

### Timestamps in query results

Records returned by `space-weather` and `space-weather-ssr` include
several timestamps:

- `<instrument>_epoch` (e.g. `mag_epoch`): the time the measurement was
  taken onboard the spacecraft.
- `ttj2000ns`: the `<instrument>_epoch` converted to nanoseconds since
  the J2000 epoch (2000-01-01T12:00:00), on the Terrestrial Time (TT)
  timescale.
- `time_utc`: the UTC time the spacecraft created the packet. The
  `--time_utc_start` and `--time_utc_end` arguments filter on this field.

## Importing as a package

```python
import ialirt_data_access

# Search for files
results = ialirt_data_access.log_query(year="2024", doy="045", instance="1")
```

## Configuration

### Data Access URL

To change the default URL that the package accesses, you can set
the environment variable `IALIRT_DATA_ACCESS_URL` or within the
package `ialirt_data_access.config["DATA_ACCESS_URL"]`. The default
is the production server `https://ialirt.imap-mission.com`.

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

For troubleshooting support, go to [this page.](https://github.com/IMAP-Science-Operations-Center/ialirt-data-access/tree/main/docs/troubleshooting.md)
