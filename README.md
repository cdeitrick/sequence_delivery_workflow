sequence_delivery_workflow

# Usage

Quickly demux and upload a folder of raw illumina data
```bash
python sequence_delivery_workflow --input [folder] --output [output_folder]
```

The script will display a url where the user can copy-paste into a browser window. The user then has to allow the program to access the box.com folder where the files will be stored.
Finally, the webpage will be redirected to another page, which may display a "page not found" error. Simple copy-paste the url of that page into the console and hit Enter.
