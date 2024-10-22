import pygsheets
import pandas as pd
from logging import getLogger


logger = getLogger()


def load_sheet_from_table(file_content, sheet_name="Список участников"):
    return pd.read_excel(file_content, sheet_name=sheet_name).fillna(0)


def write_data_to_table(df_data, google_token, table_id, sheet_name):
    if google_token and sheet_name and table_id:
        gc = pygsheets.authorize(service_file=google_token)
        sh = gc.open_by_key(table_id)
    else:
        logger.error("Check google_token, sheet_name, table_id existance: %s %s %s",
                     *(google_token, table_id, sheet_name))
        return False

    try:
        ws = sh.worksheet('title', sheet_name)
    except pygsheets.WorksheetNotFound:
        ws = sh.add_worksheet(title=sheet_name)
        logger.info("Create new sheet: %s" % sheet_name)
    else:
        logger.info("Get existing sheet: %s", sheet_name)

    ws.set_dataframe(df_data, 'A1', copy_head=True)
    return True
