import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tabulate import tabulate

#root scope
LECTURES_PATH = "//div[@class='section-home']/div/div[2]/div/div/div/div"
DIALOG_PATH = "//div[@class='modal-body-content downloadModal']"
RES_PATH = "//div[@class='downloadOptions']/div[1]/div/div/select/option"
DOWNLOAD_URL_PATH = "//div[@class='modal-footer ']/div[@class='right']/a"
CLOSE_DIALOG_PATH = "//div[@class='modal-footer ']/div[@class='left']/a"

#lecture scope
DOWNLOAD_LINK_PATH = "./div/div/div[2]/ul/li[2]/a"
TIME_PATH = "./span/span"
OPEN_DIALOG_PATH = "./div/div"


def login(driver):
    driver.get("https://echo360.org")
    driver.find_element_by_id("email").send_keys("{}@illinois.edu".format(NETID))
    driver.find_element_by_id("submitText").click()
    driver.find_element_by_id("j_username").send_keys(NETID)
    driver.find_element_by_id("j_password").send_keys(PW)
    driver.find_element_by_id("submit_button").click()
    

def get_courses(driver):
    get_name = lambda el: el.get_attribute("text").strip().splitlines()[-1].strip()
    get_url = lambda el: el.get_attribute("href")
    courses = driver.find_elements_by_xpath(".//body/div[@class='nav legacy']/ul/li[2]/div/div/ul/li/a")
    return [(get_name(course), get_url(course)) for course in courses][:-1]


def download_lectures(driver):
    def wait_then(f):
        return WebDriverWait(driver, 5).until(f)
    def rename_file(url, download_name):
        unnamed_url = url[:url.find("fileName=")]
        return "{}fileName={}".format(unnamed_url, download_name)
    lectures = wait_then(lambda _: driver.find_elements_by_xpath(LECTURES_PATH))
    for lecture in lectures:
        date, time = wait_then(lambda _: lecture.find_elements_by_xpath(TIME_PATH))
        lecture.find_element_by_xpath(OPEN_DIALOG_PATH).click()
        wait_then(lambda _: lecture.find_element_by_xpath(DOWNLOAD_LINK_PATH)).click()
        dialog = wait_then(lambda _: driver.find_element_by_xpath(DIALOG_PATH))
        dialog.find_elements_by_xpath(RES_PATH)[-1].click()
        raw_url = wait_then(lambda _: driver.find_element_by_xpath(DOWNLOAD_URL_PATH).get_attribute("href"))
        download_name = "{}, {}.mp4".format(date.text, time.text)
        url = rename_file(raw_url, download_name)
        driver.get(url)
        driver.find_element_by_xpath(CLOSE_DIALOG_PATH).click()

def make_driver():
	return webdriver.Chrome()

def select_course(courses):
	def print_courses():
		cols = ["#", "Course"]
		rows = [[idx, name] for idx, (name, _) in enumerate(courses)]
		print(tabulate(rows, cols, tablefmt="grid"))
	print("Select course by entering the row #: ")
	print_courses()
	course_selected =  int(input())
	if course_selected < 0 or course_selected > len(courses):
		print("Invalid Choice")
		exit(1)
	return course_selected

def get_credentials():
	print("I-L-L!, please enter your NetID: ")
	global NETID, PW
	NETID = input().strip().lower()
	PW = getpass.getpass(prompt='Please enter your password: ')


def wait_till_dowloaded(driver):
	def downloads_finished(_):
	    if not driver.current_url.startswith("chrome://downloads"):
	        driver.get("chrome://downloads/")
	    return driver.execute_script("""
	        var items = downloads.Manager.get().items_;
	        if (items.every(e => e.state === "COMPLETE"))
	            return items.map(e => e.file_url);
	        """)
	WebDriverWait(driver, 1800, 1).until(downloads_finished)

def main():
	get_credentials()
	print("Connecting...")
	driver = make_driver()
	login(driver)
	courses = get_courses(driver)
	course_selected = select_course(courses)
	driver.get(courses[course_selected][1])
	download_lectures(driver)
	print("Downloading...")
	wait_till_dowloaded(driver)
	print("Done!")

if __name__ == '__main__':
	main()

