from bs4 import BeautifulSoup
from selenium import webdriver

driver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver")
child_page_driver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver")
start_url = 'https://www.scrumalliance.org/community/certificant-directory.aspx'
next_url = 'https://www.scrumalliance.org/community/certificant-directory.aspx?firstname=&lastname=&email=&location=&company=&csm=False&csd=False&csp=False&cspo=False&cst=False&ctc=False&cec=False&rep=False&author=False&orderby=&sortdir=&page='
driver.get(url=start_url)
page_count = 100
present_page = 1
data = []

class AgileRow:
    def __init__(self):
        self.Name = ""
        self.Certification = ""
        self.Location = ""
        self.Company = ""
        self.Link = ""
        self.Picture = ""
        self.OutLinks = []

    def __str__(self):
        return "name="+self.Name \
               + ", Certification=" + self.Certification \
               + ", Location=" + self.Location \
               + ", Company=" + self.Company \
               + ", Link=" + self.Link \
               + ", Picture=" + self.Picture \
               + ", OutLinks=" + ','.join(map(str, self.OutLinks))


while present_page < page_count:
    soup = BeautifulSoup(driver.page_source, "html.parser")
    tables = soup.findAll('table')
    if len(tables) == 0:
        continue
    for table in tables:
        rows = table.findAll(lambda tag: tag.name == 'tr')
        links = table.findAll('a')
        for row in rows:
            index = rows.index(row) + 3
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            if len(cols) is not 4:
                continue
            agile_row = AgileRow()
            agile_row.Name = cols[0]
            agile_row.Certification = cols[1]
            agile_row.Location = cols[2]
            agile_row.Company = cols[3]
            agile_row.Link = 'https://www.scrumalliance.org' + links[index].get('href')
            child_page_driver.get('https://www.scrumalliance.org' + agile_row.Link)
            child_soup = BeautifulSoup(child_page_driver.page_source, "html.parser")
            picture = child_soup.select("#wrap > div.container > div.primary-content-area > div > div > div.span10.span9-tablet.span9-minitab > div.span10.span12-tablet.span12-minitab > div.profile_page_header.row-fluid.row-fluid-minitab > div.span4.span5-tablet.span6-minitab.span12-phone > img")
            if len(picture) > 0:
                agile_row.Picture = picture[0]["src"]
            outlinks = child_soup.find_all('a', href=True)
            if len(outlinks) > 0:
                for link in outlinks:
                    if link["href"].startswith("/") \
                            or link["href"].startswith("#") \
                            or "scrumalliance" in link["href"].lower() \
                            or "agilecareers" in link["href"] \
                            or "Scrum-Alliance" in link["href"] \
                            or "http://plus.google.com/117075062329893756789" in link["href"]:
                        continue
                    agile_row.OutLinks.append(link["href"])
            if "Indiana" in agile_row.Location.lower() or "IN" in agile_row.Location.lower():
                print(unicode(agile_row))
    present_page = present_page + 1
    next_url = next_url + str(present_page)
    driver.get(next_url)
