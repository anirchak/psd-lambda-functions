import boto3
import os
import pandas as pd
import shutil
import time

from dotenv import load_dotenv
from queue import Queue
from selenium import webdriver
from selenium.webdriver.common.by import By
from tempfile import mkdtemp

from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

SSOCs = [
  1221, 1222, 1330, 1349, 2122, 2123, 2152, 2153, 2166, 2431, 2433, 2511, 2512,
  2514, 2515, 2519, 2521, 2522, 2523, 2524, 2529, 2641, 2642, 2651, 2654, 2656,
  3114, 3440, 3511, 3512, 3514, 3521, 3522, 3523, 3620, 4132, 4315, 5142, 7421,
  7422
]

def login(driver):
  driver.get("https://labourinsight.lightcast.io/sgp")

  time.sleep(5)

  email_field = driver.find_element(By.ID, "loginEmail")
  email_field.click()
  email_field.send_keys(os.environ['BG_EMAIL'])

  password_field = driver.find_element(By.ID, "Password")
  password_field.click()
  password_field.send_keys(os.environ['BG_PASSWORD'])

  login_button = driver.find_element(By.ID, "submit")
  login_button.click()

def get_skill_spotlight(driver, actions, wait):
  wait.until(
    EC.element_to_be_clickable(
      (By.XPATH, '//*[contains(text(), "Skill Spotlight")]')))
  skill_spotlight = driver.find_element(
    By.XPATH, '//*[contains(text(), "Skill Spotlight")]')
  actions.move_to_element(skill_spotlight).click().perform()

  wait.until(
    EC.element_to_be_clickable(
      (By.XPATH, '//button[contains(text(), "Start")]')))
  start_button = driver.find_element(By.XPATH,
                                     '//button[contains(text(), "Start")]')
  start_button.click()

  time.sleep(1)
  wait.until(
    EC.element_to_be_clickable((By.XPATH, '//div[@id="accordionIndustry"]')))

  occupation_dropdown = driver.find_element(
    By.XPATH, '//div[@id="accordionOccupation"]')

  occupation_dropdown.click()

  # Select SSOC as input
  driver.find_element(By.XPATH, '//a[text()="SSOC Occupations"]').click()

  ssoc_input = driver.find_element(By.XPATH, '//input[@id="ssocCodeOptions"]')
  ssoc_input.click()  # give focus

  for ssoc in SSOCs:
    ssoc_input.send_keys(ssoc)

    time.sleep(1)
    driver.find_element(By.XPATH, f'//li[text()="{ssoc}"]').click()

    # add to list
    add_button = driver.find_element(By.XPATH,
                                     '//button[@id="btn-add-soccode"]')
    add_button.click()

  time.sleep(1)
  wait.until(
    EC.element_to_be_clickable(
      (By.XPATH, '//button[@id="showSnapshotReport"]')))
  apply_button = driver.find_element(By.XPATH,
                                     '//button[@id="showSnapshotReport"]')
  apply_button.click()

  time.sleep(1)
  wait.until(
    EC.element_to_be_clickable((By.XPATH, '//div[@id="export-section"]')))
  export_button = driver.find_element(By.XPATH, '//div[@id="export-section"]')
  actions.move_to_element(export_button).click().perform()

  wait.until(
    EC.element_to_be_clickable(
      (By.XPATH,
       '//div[@id="export-section"]//li[@data-bind="click: exportExcel"]')))

  download_button = driver.find_element(
    By.XPATH,
    '//div[@id="export-section"]//li[@data-bind="click: exportExcel"]')
  download_button.click()

  time.sleep(3)

  # wait = WebDriverWait(driver, 60)
  download_path = os.path.expanduser('~')
  repo_name = "DeliriousTangibleDiskdrive"
  file_name = "Skill Spotlight.xlsx"
  file_path = download_path + "/Downloads/" + file_name
  # wait.until(EC.presence_of_file(file_path))
  # time.sleep(5)
  time_counter = 0
  while not os.path.exists(file_path):
    time.sleep(1)
    time_counter += 1
    if time_counter > 20: break

  new_file_path = os.path.join(download_path, repo_name, file_name)
  shutil.move(file_path, new_file_path)


def get_occupation_analysis(driver, actions, wait):
  wait.until(
    EC.element_to_be_clickable(
      (By.XPATH, '//*[contains(text(), "Occupation Analysis")]')))
  skill_spotlight = driver.find_element(
    By.XPATH, '//*[contains(text(), "Occupation Analysis")]')
  actions.move_to_element(skill_spotlight).click().perform()

  wait.until(
    EC.element_to_be_clickable(
      (By.XPATH, '//button[contains(text(), "Start")]')))
  start_button = driver.find_element(By.XPATH,
                                     '//button[contains(text(), "Start")]')
  start_button.click()

  for ssoc in SSOCs:
    driver.find_element(By.XPATH, '//div[@id="titleFilterSource"]').click()

    driver.find_element(By.XPATH, '//span[text()="Switch to SSOC"]').click()

    ssoc_input = driver.find_element(By.XPATH,
                                     '//input[@id="selectAnzscoOccupation"]')
    ssoc_input.click()

    ssoc_input.send_keys(ssoc)

    driver.find_element(By.XPATH,
                        f'//li[contains(text(), "({ssoc})")]').click()

    driver.find_element(By.XPATH, '//button[text()="Apply Filters"]').click()

    driver.find_element(By.XPATH,
                        '//div[@id="Workforce-export-section"]').click()

    driver.find_element(By.XPATH, '//span[text()="Excel"]').click()

    time.sleep(5)

    driver.find_element(By.XPATH,
                        '//a[@class="dashboard-filter-reset"]').click()

    download_path = os.path.expanduser('~')
    repo_name = "DeliriousTangibleDiskdrive"
    file_name = "Occupation Analysis.xlsx"
    file_path = download_path + "/Downloads/" + file_name
    # wait.until(EC.presence_of_file(file_path))
    # time.sleep(5)
    time_counter = 0
    while not os.path.exists(file_path):
      time.sleep(1)
      time_counter += 1
      if time_counter > 20: break

    new_file_name = "Occupation Analysis_ssoc_" + str(ssoc) + ".xlsx"
    new_file_path = os.path.join(download_path, repo_name, new_file_name)
    shutil.move(file_path, new_file_path)


def consolidate_occupation_analysis_skills():
  occupation_analysis_files = [
    file for file in os.listdir() if 'Occupation Analysis_ssoc_' in file
  ]

  columns = [
    'SSOC', 'Skill', 'Skill Type', 'Description',
    'Job Postings Requesting (Last 12 Months)', 'Projected Growth (2 Years)'
  ]
  output = pd.DataFrame(columns=columns)
  for file in occupation_analysis_files:
    # Read 'Occupation Analysis' report
    skill_sheet = pd.read_excel(file, 'Skills', skiprows=7)

    # Add 'SSOC' column by extracting the ssoc from the filename
    skill_sheet['SSOC'] = file[-9:-5]

    # Drop 'Salary Premium' column
    skill_sheet.drop(labels=['Salary Premium'], axis=1, inplace=True)

    # Add rows to output df
    # output = pd.concat([output, skill_sheet])

    if not os.path.isfile('Occupation Analysis Skills.csv'):
      skill_sheet.to_csv('Occupation Analysis Skills.csv', header=True)
    else:
      skill_sheet.to_csv('Occupation Analysis Skills.csv',
                         mode='a',
                         header=False)


def consolidate_time_series_analysis():
  time_series_analysis_files = [
    file for file in os.listdir() if 'Time Series Analysis_ssoc_' in file
  ]

  columns = ['4D SSOC', '5D Job Title', 'Period', 'Job Postings']
  for file in time_series_analysis_files:
    data_sheet = pd.read_excel(file, 'Data')
    data_sheet.drop(labels=[c for c in data_sheet.columns if 'Unnamed' in c],
                    inplace=True,
                    axis=1)

    output = pd.DataFrame(columns=columns)
    for i in range(1, len(data_sheet.columns)):
      for j in range(data_sheet.shape[0]):
        output.loc[len(output)] = [
          file[-9:-5], data_sheet.columns[i], data_sheet.iloc[j, 0],
          data_sheet.iloc[j, i]
        ]

    if not os.path.isfile('Time Series Analysis.csv'):
      output.to_csv('Time Series Analysis.csv', header=True, index=False)
    else:
      output.to_csv('Time Series Analysis.csv',
                    mode='a',
                    header=False,
                    index=False)


def get_time_series(driver, wait):
  driver.find_element(By.XPATH,
                      '//a[contains(text(), "Create Reports")]').click()

  time.sleep(3)

  wait.until(
    EC.element_to_be_clickable((By.XPATH, '//div[@id="selectReportFocus"]')))

  time.sleep(5)

  driver.find_element(By.XPATH, '//div[@id="selectReportFocus"]').click()

  time.sleep(1)

  driver.find_element(By.XPATH,
                      '//a[@id="Time Series Analysis_anchor"]').click()

  driver.find_element(By.XPATH, '//div[@id="accordionOccupation"]').click()

  driver.find_element(By.XPATH, '//a[text()="SSOC Occupations"]').click()

  for ssoc in SSOCs:
    ssoc_input = driver.find_element(By.XPATH,
                                     '//input[@id="JTAndOccsOnetCode"]')
    ssoc_input.click()  # give focus

    ssoc_input.send_keys(ssoc)

    time.sleep(1)
    driver.find_element(By.XPATH, f'//a[contains(text(), "{ssoc}")]').click()
    time.sleep(1)

    # add to list
    add_button = driver.find_element(By.XPATH,
                                     '//button[@id="btn-add-soccode"]')
    add_button.click()

    try:
      driver.find_element(By.XPATH, '//button[@id="showReport"]').click()

      time.sleep(3)
    except NoSuchElementException:
      driver.find_element(By.XPATH,
                          '//button[@id="ParameterUpdateButton"]').click()
    finally:
      driver.find_element(
        By.XPATH, '//span[contains(text(), "Total Postings")]').click()

      driver.find_element(
        By.XPATH,
        '//span[contains(text(), "Top Occupations (SSOC)")]').click()

      driver.find_element(By.XPATH,
                          '//span[contains(text(), "5-D SSOC 2020")]').click()

      time.sleep(2)

      driver.find_element(
        By.XPATH,
        '//div[@id="liveSeriesSubPopupDataOccupation00"]/ul/li[2]').click()

      driver.find_element(By.XPATH,
                          '//span[contains(text(), "Annually")]').click()

      time.sleep(2)

      driver.find_element(
        By.XPATH, '//div[@id="liveSeriesIntervalPopup0"]/ul/li[1]').click()

    time.sleep(3)

    wait.until(
      EC.element_to_be_clickable(
        (By.XPATH, '//div[@id="Workforce-export-section"]')))
    driver.find_element(By.XPATH,
                        '//div[@id="Workforce-export-section"]').click()
    driver.find_element(By.XPATH, '//span[text()="Excel"]').click()

    time.sleep(5)

    driver.find_element(
      By.XPATH, '//button[contains(text(), "Create/edit Report")]').click()
    time.sleep(1)

    occupation_accordion = driver.find_element(
      By.XPATH, '//div[@id="accordionOccupation"]')
    if 'expanded' not in occupation_accordion.get_attribute('class'):
      occupation_accordion.click()

    time.sleep(1)
    driver.find_element(By.XPATH, '//a[text()="SSOC Occupations"]').click()

    driver.find_element(By.XPATH, '//span[@class="combineImgText"]').click()

    download_path = os.path.expanduser('~')
    repo_name = "DeliriousTangibleDiskdrive"
    file_name = "Time Series Analysis.xlsx"
    file_path = download_path + "/Downloads/" + file_name
    time_counter = 0
    while not os.path.exists(file_path):
      time.sleep(1)
      time_counter += 1
      if time_counter > 20:
        print('no file downloaded')
        break

    downloaded_file_path = [os.path.join(dp, f) for dp, dn, filenames in os.walk('/tmp/') for f in filenames if 'Time' in f][0]
    # s3_client = boto3.client('s3', aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
    s3_client = boto3.client('s3')
    s3_client.upload_file(downloaded_file_path, 'psd-dashboard-data', f'time_series_analysis_{int(time.time())}.xlsx')

    print(', '.join([os.path.join(dp, f) for dp, dn, filenames in os.walk('/tmp/') for f in filenames if 'Time' in f]))
  
    url = s3_client.generate_presigned_url(ClientMethod='get_object', Params={ 'Bucket': 'psd-dashboard-data', 'Key': f'time_series_analysis_{int(time.time())}xlsx' })
    print(url)

    return ', '.join([os.path.join(dp, f) for dp, dn, filenames in os.walk('/') for f in filenames if 'Time' in f])
  
    new_file_name = "Time Series Analysis_ssoc_" + str(ssoc) + ".xlsx"
    new_file_path = os.path.join(download_path, repo_name, new_file_name)
    shutil.move(file_path, new_file_path)

  time.sleep(10)

  
def handler(event=None, context=None):
  load_dotenv()
  
  try:
    options = webdriver.ChromeOptions()
    options.binary_location = '/opt/chrome/chrome'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.add_argument(f"--user-data-dir={mkdtemp()}")
    options.add_argument(f"--data-path={mkdtemp()}")
    options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    options.add_argument("--remote-debugging-port=9222")
    prefs = {"profile.default_content_settings.popups": 0,    
            "download.default_directory":r"/tmp",
            "download.prompt_for_download": False,
            "directory_upgrade": True}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome("/opt/chromedriver", options=options)

    login(driver)

    actions = ActionChains(driver)
    wait = WebDriverWait(driver, 10)

    if type == "Regional":
      wait.until(
        EC.element_to_be_clickable(
          (By.XPATH, '//*[contains(text(), "Regional Scan")]')))
      regional_scan = driver.find_element(
        By.XPATH, '//*[contains(text(), "Regional Scan")]')
      actions.move_to_element(regional_scan).click().perform()

      wait.until(
        EC.element_to_be_clickable(
          (By.XPATH, '//button[contains(text(), "Start")]')))
      start_button = driver.find_element(By.XPATH,
                                        '//button[contains(text(), "Start")]')
      start_button.click()
    elif type == "Skill":
      get_skill_spotlight(driver, actions, wait)
      return
    elif type == "Occupation Analysis":
      get_occupation_analysis(driver, actions, wait)
      return
    elif type == "Time Series":
      return get_time_series(driver, wait)
  except Exception as e:
    print("Exception occured: ", e)

# handler()
