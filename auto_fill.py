import random
import time
from datetime import datetime
from selenium import webdriver
#from selenium.webdriver.edge.webdriver import WebDriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import yaml

MIN_SPAN_TIME_MS = 3000


def autofill(shop: str, locale: str, date: datetime)->str:
	if len(locale) > 2:
		locale = locale[0:2]
	locale.capitalize()
	# ==================INIT WEBDRIVER==================
	options = Options()
	options.add_argument('--headless=new')

	driver = webdriver.Chrome(options=options)
	driver.get("https://www.wakakakaka.com")

	iframe = WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, 'qiddiqqiddiq.com')]"))
	)
	driver.switch_to.frame(iframe)

	# ==================PAGE1:SHOP CHECK==================
	shop_input = WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.XPATH, "//input[contains(@name, 'QID')]")))
	shop_input.send_keys(shop)

	time.sleep(random.randint(100, MIN_SPAN_TIME_MS + 2000) / 1000)

	next_button = driver.find_element(By.XPATH, "//input[@id='NextButton']")
	next_button.click()

	# ==================2 RECEIPT CHECK==================
	shop_l_selector = WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.XPATH, "//select[contains(@class, 'ChoiceStructure Selection')]")))
	select = Select(shop_l_selector)
	select.select_by_visible_text(locale)
	time.sleep(random.randint(100, MIN_SPAN_TIME_MS) / 1000)

	date_input = WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.XPATH, "//input[contains(@name, 'QR~QID118~2~TEXT')]")))
	driver.execute_script(f"arguments[0].value = '{date.strftime('%m/%d/%Y')}';", date_input)
	time.sleep(random.randint(100, MIN_SPAN_TIME_MS) / 1000)

	hh_selector = driver.find_element(By.XPATH, "//select[contains(@id, 'QR~QID8#1~1')]")
	select = Select(hh_selector)
	select.select_by_visible_text(date.strftime("%I"))
	time.sleep(random.randint(100, MIN_SPAN_TIME_MS) / 1000)

	mm_selector = driver.find_element(By.XPATH, "//select[contains(@id, 'QR~QID8#2~1')]")
	select = Select(mm_selector)
	select.select_by_visible_text(date.strftime("%M"))
	time.sleep(random.randint(100, MIN_SPAN_TIME_MS) / 1000)

	ii_selector = driver.find_element(By.XPATH, "//select[contains(@id, 'QR~QID8#3~1')]")
	select = Select(ii_selector)
	select.select_by_visible_text(date.strftime("%p"))
	time.sleep(random.randint(100, MIN_SPAN_TIME_MS) / 1000)

	next_button = driver.find_element(By.XPATH, "//input[@id='NextButton']")
	next_button.click()
	# ==================SURVEY FILL==================
	with open('./config.yaml') as fp:
		survey_seq = yaml.load(fp, yaml.SafeLoader)

	for d in survey_seq:
		perform_dict(d, driver)

	strong_element = WebDriverWait(driver, 10).until(
					EC.presence_of_element_located((By.XPATH, '//*[@id="EndOfSurvey"]/strong[1]')))

	# ==================END OF SURVEY==================
	validation_code = strong_element.text.split(":")[1].strip()  # Extract the code
	print("Validation Code:", validation_code)

	# ==================DONE==================
	driver.quit()
	return validation_code


def perform_dict(sub_seq: dict, driver: WebDriver):
	t = sub_seq['type']
	if t == 'choice':
		can_be_ignore=sub_seq.get('can_be_ignore',False)
		for ch in sub_seq['choices']:
			try:
				radio_button = WebDriverWait(driver, 10).until(
					EC.presence_of_element_located((By.ID, ch)))
				ActionChains(driver).click(radio_button).perform()
				time.sleep(random.randint(500, MIN_SPAN_TIME_MS) / 1000)
			except TimeoutException:
				if can_be_ignore:
					continue
				else:
					raise
		if not sub_seq.get('no_next_button', False):
			next_button = driver.find_element(By.XPATH, "//input[@id='NextButton']")
			next_button.click()
		return
	elif t == 'text':
		data_input = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.ID, sub_seq['label'])))
		data_input.send_keys(sub_seq['content'])
		time.sleep(random.randint(100+len(sub_seq['content'])*100, MIN_SPAN_TIME_MS+len(sub_seq['content'])*100) / 1000)
		if not sub_seq.get('no_next_button', False):
			next_button = driver.find_element(By.XPATH, "//input[@id='NextButton']")
			next_button.click()
		return
	else:
		raise Exception("Invalid Type when decoding config.")

