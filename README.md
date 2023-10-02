# Import pruffme statistics to ETU attendance

Requirements:
* Python3.9+

Install the requirements using the `pip3 install -r requirements.txt` command.

Run the script: `python3 attendance.py -c <cookie_file> -a <csv_from_pruffme> -d <date_of_the_week>`.
Arguments:
* -c/--cookies: cookies after authorization, see `cookie.json` file;
* -a/--attendance: csv table from pruffme;
* -d/--date: the week to get information about (set to Wednesday day). Example: `2023-09-26`.
