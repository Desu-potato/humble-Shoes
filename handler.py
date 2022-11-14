from env import DOMEN, DOMEN_FOR_DETAILS, BUTTON_DETALS_PATH, REQUEST_DELAY, UR_WEBHOOK
from bs4 import BeautifulSoup
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import sqlite3, time, requests
from datetime import datetime
import json
options = Options()
options.headless = True


def send_webhook(content):
    url = UR_WEBHOOK
    payload = json.dumps(content)
    headers = {
        'Content-Type' : 'application/json',
        'Accept' : '*/*'
    }
    requests.request("POST", url, headers=headers, data=payload)



def main_protocol():
    i = 0

    while True:
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        print("Cycle: ", i, date_time)
        time.sleep(REQUEST_DELAY)
        site = send_request()
        array = rebrand_of_information(site)
        if bool(array):
            main_functions_wrapper(array)
        i = i+1


def return_inner_id(record):
    array = record['Location'].split(".")
    test = array[0][len(array[0]) - 13:].upper()
    return test


def add_to_database_if_not_exist(records):

    newNotification = []
    for record in records:
        if check_if_in_base(record):
            add_to_database(record)
            record['Inner_id'] = return_inner_id(record)
            newNotification.append(record)


    return newNotification

def take_detail_information():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    query = '''
                                select `id`, `location` from `shoes`

                                '''
    r = cur.execute(query)

    workingArray = []
    for record in r:
        id, location = record
        array = location.split(".")
        test = array[0][len(array[0])-13:].upper()
        workingArray.append({ "Id" : str(id), "Details" : { "Inner_ID": test} })

    for record in workingArray:
        query = '''
                                        select `inner_ID` from `shoes` where `id` = "'''+record['Id']+'''"'''


        r = cur.execute(query)
        enum = r.fetchall()
        id = enum[0]
        if not bool(id[0]):
            query = '''UPDATE `shoes` SET `inner_id`="'''+record['Details']['Inner_ID']+'''" WHERE `id` = "'''+record['Id']+'''"'''
            cur.execute(query)
            conn.commit()

    conn.commit()
    conn.close()



def main_functions_wrapper(records):
    newRecordsNotification =  add_to_database_if_not_exist(records)
    newDeprecitedNotification = check_what_in_base_is_depicated(records)
    newChangesNotification = []
    for record in records:
        newChangesNotification.append(check_what_diffrent(record))
        update_record_in_database(record)

    take_detail_information()


    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    if bool(newRecordsNotification):

        for enum in newRecordsNotification:
            content = {
              "type": 3,
              "id": "658822586720976555",
              "name": "Webhook",
              "avatar": "689161dc90ac261d00f1608694ac6bfd",
              "channel_id": None,
              "guild_id": None,
              "application_id": "658822586720976555",
              "embeds": [
                {
                  "title": ""+enum['Model'],
                  "url": ""+DOMEN_FOR_DETAILS+enum['Location'],
                  "thumbnail": {
                    "url": ""+enum['Picture']
                  },
                  "fields": [
                        {
                            "name": "SKU",
                            "value": ""+enum['Inner_id']
                        },
                        {
                            "name": "Price",
                            "value": ""+enum['Price']
                        },
                        {
                            "name": "Relese date",
                            "value": ""+enum['Available']
                        },
                        {
                            "name": "Stock level",
                            "value": "TEST-RELESE"
                        }

                        ],
                    "footer": {
                        "text": ""+date_time
                  }
                  }
              ]

            }

            send_webhook(content)

    if bool(newDeprecitedNotification):
        for enum in newDeprecitedNotification:
            content = {
                "type": 3,
                "id": "658822586720976555",
                "name": "Webhook",
                "avatar": "689161dc90ac261d00f1608694ac6bfd",
                "channel_id": None,
                "guild_id": None,
                "application_id": "658822586720976555",
                "embeds": [
                    {
                        "title": "" + enum['Model'],
                        "url": "" + DOMEN_FOR_DETAILS + enum['Location'],
                        "thumbnail": {
                            "url": "" + enum['Picture']
                        },
                        "fields": [
                            {
                                "name": "OH NO!",
                                "value": "The offer seems to have disappeared."
                            },
                            {
                                "name": "SKU",
                                "value": "" + enum['Inner_id']
                            },
                            {
                                "name": "Price",
                                "value": "" + enum['Price']
                            },
                            {
                                "name": "Relese date",
                                "value": "" + enum['Available']
                            },
                            {
                                "name": "Stock level",
                                "value": "TEST-RELESE"
                            }

                        ],
                        "footer": {
                            "text": "" + date_time
                        }
                    }
                ]

            }

            send_webhook(content)


    for enum in newChangesNotification:

        if len(enum) != 1:
            conn = sqlite3.connect("database.db")
            cur = conn.cursor()
            query = '''
                                select * from `shoes` where  `id` = "''' + str(enum[0]['id']) + '''"

                                '''
            r = cur.execute(query)

            id_record, price, brand, model, available, location, picture, inner_id = r.fetchall()[0]
            conn.commit()
            conn.close()

            content = {
                "type": 3,
                "id": "658822586720976555",
                "name": "Webhook",
                "avatar": "689161dc90ac261d00f1608694ac6bfd",
                "channel_id": None,
                "guild_id": None,
                "application_id": "658822586720976555",
                "embeds": [
                    {
                        "title": "" + model,
                        "url": "" + DOMEN_FOR_DETAILS + location,
                        "thumbnail": {
                            "url": "" + picture
                        },
                        "fields": [
                            {    "name": "Something changed!",
                                 "value" : str(enum[1]) +""
                            },
                            {
                                "name": "SKU",
                                "value": "" + inner_id
                            },
                            {
                                "name": "Price",
                                "value": "" + price
                            },
                            {
                                "name": "Relese date",
                                "value": "" + available
                            },
                            {
                                "name": "Stock level",
                                "value": "TEST-RELESE"
                            }

                        ],
                        "footer": {
                            "text": "" + date_time
                        }
                    }
                ]

            }

            send_webhook(content)









def check_what_in_base_is_depicated(records):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    query = '''
                            select `id`, `location` from `shoes`

                            '''
    r = cur.execute(query)
    records_from_database = r.fetchall()

    locationArray = []
    for record in records:
        locationArray.append(record['Location'])


    depricated = []
    for id, location in records_from_database:

        if not location in locationArray:
            depricated.append(id)

    depricatedArray = []
    if bool(depricated):
        for record in depricated:
            query = '''
                                                   select * FROM `shoes` WHERE `id` = "''' + str(record) + '''"

                                                   '''
            r = cur.execute(query)
            conn.commit()
            id_record, price, brand, model, available, location, picture, inner_id = r.fetchall()[0]
            depricatedArray.append({"Price" : price, "Brand" : brand, "Model": model,  "Available": available, "Location": location, "Picture": picture, "Inner_id" : inner_id })


            query = '''
                                       DELETE FROM `shoes` WHERE `id` = "'''+str(record)+'''"

                                       '''
            cur.execute(query)
            conn.commit()


    conn.commit()
    conn.close()
    return depricatedArray




def check_what_diffrent(record):
        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        diffrences = []
        query = '''
                select * from `shoes` where  `location` = "''' + record['Location'] + '''"
    
                '''
        r = cur.execute(query)

        id_record, price, brand, model, available, location, picture, inner_id  = r.fetchall()[0]
        conn.commit()
        conn.close()
        diffrences.append({"id" : id_record})
        if record['Price'] != price:
            diffrences.append({"Price" : record['Price'], "Previous" : price})
        if record['Brand'] != brand:
            diffrences.append({"Brand" : record['Brand'], "Previous" : brand})
        if record['Model'] != model:
            diffrences.append({"Model" : record['Model'], "Previous" : model})
        if record['Available'] != available:
            diffrences.append({"Available" : record['Available'], "Previous" : available})
        if record['Picture'] != picture:
            diffrences.append({"Picture" : record['Picture'], "Previous" : picture})

        return diffrences



def update_record_in_database(record):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    query = '''
                    select * from `shoes` where  `location` = "''' + record['Location'] + '''"

                    '''
    r = cur.execute(query)
    id_record, price, brand, model, available, location, picture, inner_id  = r.fetchall()[0]
    id_record = str(id_record)
    if record['Price'] != price:
        query = '''
                 UPDATE `shoes` SET `price`= "'''+record['Price']+'''" WHERE `id` = ''' + id_record + '''
              '''
        cur.execute(query)
        conn.commit()
    if record['Brand'] != brand:
        query = '''
                         UPDATE `shoes` SET `brand`="'''+record['Brand']+'''" WHERE `id` = ''' + id_record + '''
                      '''
        cur.execute(query)
        conn.commit()
    if record['Model'] != model:
        query = '''
                         UPDATE `shoes` SET `model`="'''+record['Model']+'''" WHERE `id` = ''' + id_record + '''
                      '''
        cur.execute(query)
        conn.commit()
    if record['Available'] != available:
        query = '''
                         UPDATE `shoes` SET `available`="'''+record['Available']+'''" WHERE `id` = ''' + id_record + '''
                      '''
        cur.execute(query)
        conn.commit()
    if record['Picture'] != picture:
        query = '''
                         UPDATE `shoes` SET `picture`="'''+record['Picture']+'''" WHERE `id` = ''' + id_record + '''
                      '''
        cur.execute(query)
        conn.commit()
    conn.commit()
    conn.close()




def check_if_in_base(record):
        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        query = '''
        select `id` from `shoes` where `location` = "'''+record['Location']+'''"
        
        '''

        r = cur.execute(query)
        test = r.fetchall()
        conn.commit()
        conn.close()
        if not (test):
            return True
        return False





def add_to_database(record):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    query = '''INSERT INTO `shoes`( `price`, `brand`, `model`, `available`, `location`, `picture` ) VALUES ( "'''+record['Price']+'''", "'''+record['Brand']+'''", "'''+record['Model']+'''", "'''+record['Available']+'''", "'''+record['Location']+'''", "'''+record['Picture']+'''")'''
    cur.execute(query)
    conn.commit()
    conn.close()

def send_request():
    browser = Firefox(options=options)

    browser.get(DOMEN)
    content = browser.page_source
    browser.close()
    return str(content)

def send_request_for_details(location):
    browser = Firefox(options=options)

    browser.get(DOMEN_FOR_DETAILS + location)

    for record in browser.find_elements("xpath", BUTTON_DETALS_PATH):
        record.click()

    content = browser.page_source
    browser.close()
    return str(content)



def send_request_for_details_mock():
    f = open("test_details.html", "r")
    return str(f.read())


def debug_open_file_to_mock() -> str:
    f = open("test.html", "r")
    return str(f.read())



def rebrand_of_information(site: str):

    soup = BeautifulSoup(site, 'lxml')

    template = soup.find_all("div", {"class":"NYErdr UyCaZm PHBKNf"})[1]
    working_array = []

    for child in template.children:
        working_array.append(child)

    rebranded_data = []
    for child in working_array:
        data = child.get_text("|")
        array = data.split("|")
        array.pop()
        array.append(child.a.get_attribute_list('href')[0])
        array.append(child.img.get_attribute_list('src')[0])



        rebranded_data.append(
            {
            "Price": array[0],
            "Brand": array[1],
            "Model": array[2],
            "Available": array[3],
            "Location": array[4],
            "Picture" : array[5],
            }
        )



    return rebranded_data





def rebrand_of_information_details(site: str, Location):
    soup = BeautifulSoup(site, 'lxml')
    r = soup.find_all("span", {"class":"_0Qm8W1 u-6V88 FxZV-M pVrzNP zN9KaA"})[-1]
    return { "Location" : Location, "Inner_id": r.text}
