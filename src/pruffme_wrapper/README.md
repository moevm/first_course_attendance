# pruffme_wrapper
## Пример запуска
(не очень хороший)
```bash
#!/bin/bash
set -e 

EXPORT_INFO_TABLE_ID="..."
EXPORT_INFO_SHEET_ID=...
EXPORT_INFO_FILE="export.csv"
PRUFFME_SESSION_ID="..."

cd $WORKSPACE/src/pruffme_wrapper

function download_csv() {
# usage: download_csv table_id sheet_id export_file_path
# csv-separatоr = ","
  table_id="$1"
  sheet_id=${2:-'0'}
  export_file=${3:-'export.csv'}
  wget -O $export_file "https://docs.google.com/spreadsheets/d/$table_id/export?gid=$sheet_id&format=csv"
}


# download table w/export info
download_csv $EXPORT_INFO_TABLE_ID $EXPORT_INFO_SHEET_ID $EXPORT_INFO_FILE


# read csv and proccess line
while IFS= read -r line 
do
  IFS=',' read -r -a current_export <<< "$line"
  # Доп. занятия по информатике,1d5fa21caa74013bffe9e098047ef99a,19.10.2024,10:30,12:00,1EnEQwEw-tK0U-zMEO_wjBh6AVGTVu2lwRPdJEGh-Y1Q,19.10

  echo "Start proccess ${current_export[0]} ${current_export[1]} ${current_export[2]}"
  echo "line: $line"
  WS_WEBINAR_ID=${current_export[1]} WS_DATE_FROM="${current_export[2]} ${current_export[3]}" WS_DATE_TO="${current_export[2]} ${current_export[4]}" \
  	WS_SESSION_ID=$PRUFFME_SESSION_ID WS_GOOGLE_TOKEN=$google_conf WS_TABLE_ID=${current_export[5]} WS_SHEET_NAME=${current_export[6]} python3 webinar_stats.py

  echo "End proccess"
done < $EXPORT_INFO_FILE

```
