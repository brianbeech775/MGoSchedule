import subprocess
import re
import xml.etree.ElementTree as ET
import time

def fetchXML(url):
	token = "e8fb745e3347158dfcc3acb5c754ba73"
	command = 'curl -s -H "Authorization: Bearer ' + token + '" -H "Accept: application/xml" ' + url

	global numRequests
	if(numRequests >= maxRequests):
		print "Max request limit exceeded! Going to sleep for 60 sec!"
		time.sleep(60)
		numRequests = 0
	numRequests += 1

	p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	return p.stdout.readlines()

def parseXML(response, termCode = 0, schoolCode = "", subjectCode = ""):
	for s in response:
		s = re.sub("<getSOC[^>]*>", "<data>", s)
		s = re.sub("</getSOC[^>]*>", "</data>", s)

		try:
			root = ET.fromstring(s)
		except:
			return

		for term in root.findall("Term"):
			termCode = term.find("TermCode").text
			termDesc = term.find("TermDescr").text
			print "Term Code: " + termCode + "\nTerm Description: " + termDesc + "\n"
			url = "http://api-gw.it.umich.edu/Curriculum/SOC/v1/Terms/" + termCode + "/Schools"
			parseXML(fetchXML(url), termCode)
		for school in root.findall("School"):
			schoolCode = school.find("SchoolCode").text
			schoolDesc = school.find("SchoolDescr").text
			print "School Code: " + schoolCode + "\nSchool Name: " + schoolDesc + "\n"
			url = "http://api-gw.it.umich.edu/Curriculum/SOC/v1/Terms/" + termCode + "/Schools/" + schoolCode + "/Subjects" 
			parseXML(fetchXML(url), termCode, schoolCode)
		for subject in root.findall("Subject"):
			subjectCode = subject.find("SubjectCode").text
			subjectDesc = subject.find("SubjectDescr").text
			print "Subject Code: " + subjectCode + "\nSubject: " + subjectDesc + "\n"
			url = "http://api-gw.it.umich.edu/Curriculum/SOC/v1/Terms/" + termCode + "/Schools/" + schoolCode + "/Subjects/" + subjectCode + "/CatalogNbrs"
			parseXML(fetchXML(url), termCode, schoolCode, subjectCode)
		for course in root.findall("ClassOffered"):
			courseNum = course.find("CatalogNumber").text
			courseName = course.find("CourseDescr").text
			print subjectCode + courseNum + ": " + courseName + "\n"

global numRequests
global maxRequests
numRequests = 0
maxRequests = 60
url = 'http://api-gw.it.umich.edu/Curriculum/SOC/v1/Terms'
parseXML(fetchXML(url))
