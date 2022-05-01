from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

#Enter character name here (example:Luz,Amity,Hooty)
name = ""
txtName = name + "Dialogue.txt"
file1 = open(txtName, "w", encoding="utf-8")
file1.truncate(0)

options = Options()
options.add_argument("--headless")

driver = webdriver.Chrome(executable_path="chromedriver.exe",options=options)
driver.get("https://theowlhouse.fandom.com/wiki/Category:Transcripts")

elements = driver.find_elements(By.CSS_SELECTOR,("div.category-page__members-wrapper a"))
i = 0
urls = []
for element in elements:
    urls.append(element.get_attribute("href"))
for url in urls:
    i += 1
    string = " \n"
    file1.write(string)
    string = str(i) + " " + url + "\n"
    print(str(i) + " " + url)
    file1.write(string)
    string = " \n"
    file1.write(string)
    driver.get(url)
    elements = driver.find_elements(By.CSS_SELECTOR,("div.mw-parser-output p"))
    j = 0
    for element in elements:
        substring = ':'
        if(substring in element.text and name in element.text[0:element.text.find(substring)]):
            file1.write(element.text + "\n")
print("FINISHED!")
file1.close()


