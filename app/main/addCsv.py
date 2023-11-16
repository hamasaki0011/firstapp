from django.db import connection
import logging
import csv
from datetime import datetime as dt

logger=logging.getLogger('development')

# SQL for adding the data
sql_insert = (
    "insert into result (measured_date, measured_value, point_id, place_id, created_date, updated_date) "
    "select * from (select cast(%s as timestamp) as measured_date, cast(%s as numeric) as measured_value, cast(%s as integer) as point_id, cast(%s as integer) as place_id, "
    "cast(%s as timestamp) as created_date, cast(%s as timestamp) as updated_date) as tmp "
    "where not exists (select * from result where point_id = cast(%s as integer) and measured_date = cast(%s as timestamp))"
)
def entry_data(cursor,file_path):
    try:
        # 2023.11.13 Read csv upload file.
        # the cursor for insert the new record.
        # cursor = <django.db.backends.postgresql.base.CursorDebugWrapper object at 0x7f13eb347880>
        # The file_path to read csv upload file
        # file_path = /usr/src/app/main/static/uploads/testNew_14.csv
        file=open(file_path,newline='')
    except IOError:
        logger.warning('対象ファイルがありません:' + file_path)
        logger.warning('DB登録は行いません:' + file_path)
    else:
        logger.info('=== > Start DB登録 ===')
        with file:
            # 2023.11.14 reader = <csv.DictReader object at 0x7f4d1b0c9a20>
            reader = csv.DictReader(file)
            print(f'addCsv#31_reader = {reader}')
            for row in reader:
                str_time = [dt.now().strftime('%Y-%m-%d %H:%M:%S')]
                add_data = []
                add_data.append(row.get('measured_date'))  # csvから辞書形式で読み取った情報
                add_data.append(row.get('measured_value'))  # csvから辞書形式で読み取った情報
                add_data.append(row.get('point_id'))  # csvから辞書形式で読み取った情報
                add_data.append(row.get('place_id'))
                add_data.extend(str_time)  # 2023.11.13 Add created_date
                add_data.extend(str_time)  # 2023.11.13 Add updated_date
                add_data.append(row.get('point_id'))  # 2023.11.13 Sensor device point ID for judgement whether the record is in the data-base or not.
                add_data.append(row.get('measured_date'))  # 2023.11.13 Re-assign measured_date in order to judge whether the record is in the data-base or not.
                # 2023.11.13 Example of above operation
                # add_data = ['2023-3-20 15:01:00', '18.0', '19', '1', '2023-11-13 15:45:54', '2023-11-13 15:45:54', '19', '2023-3-20 15:01:00']
                # add_data = ['2023-3-20 15:01:00', '22.5', '22', '1', '2023-11-13 15:45:54', '2023-11-13 15:45:54', '22', '2023-3-20 15:01:00']
                # add_data = ['2023-3-20 15:01:00', '120.5', '27', '1', '2023-11-13 15:45:54', '2023-11-13 15:45:54', '27', '2023-3-20 15:01:00']
                # add_data = ['2023-3-20 15:01:00', '25.2', '18', '2', '2023-11-13 15:45:54', '2023-11-13 15:45:54', '18', '2023-3-20 15:01:00']
                # add_data = ['2023-3-20 15:01:00', '15.6', '24', '2', '2023-11-13 15:45:54', '2023-11-13 15:45:54', '24', '2023-3-20 15:01:00']
                # add_data = ['2023-3-20 15:01:00', '14.0', '26', '2', '2023-11-13 15:45:54', '2023-11-13 15:45:54', '26', '2023-3-20 15:01:00']
                # add_data = ['2023-3-20 15:01:00', '20.0', '25', '4', '2023-11-13 15:45:54', '2023-11-13 15:45:54', '25', '2023-3-20 15:01:00']
                logger.debug('add_data = ' + str(add_data))
                
                location_id =add_data[3]
                print(f"addCsv#53_add_data = {add_data}")
                print(f"addCsv#54_location_id = {add_data[3]}")
                
                # 2023.11.13 Insert the record.
                cursor.execute(sql_insert, add_data)
                
            # # 2023.11.14 Check location_id
            # location_id = add_data[3]
            # print(f'addCsv#57_location_id = {location_id}')            
            logger.info("=== End DB登録 < ===")

# Register the data in csv file to DataBase
def insert_csv_data(file_path):
    logger.info('=== csvデータ登録開始 ===')

    with connection.cursor() as cursor:
        entry_data(cursor,file_path)

    logger.info('=== csvデータ登録処理終了 ===')