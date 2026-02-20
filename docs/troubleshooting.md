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

## Additional issues

If you encounter any issues not covered in this page, please create an issue within this repository by clicking the Issues tab and then "New Issue." There is a template for bug reporting you can utilize. Please include as many details as possible.
