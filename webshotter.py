#!/usr/bin/python
# webshotter.py - create web page screenshots
# with code from http://stackoverflow.com/questions/18067021/how-do-i-generate-a-png-file-w-selenium-phantomjs-from-a-string
#
# by julio // blog.whatever.io

from selenium import webdriver
import datetime
import os
import sys
import argparse
import threading
import Queue

# define global variables
queue = Queue.Queue()
height = 0
width = 0
VERBOSE = False

class ThreadScreenshotter(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        global height
        global width

        while True:
            url = self.queue.get()
            print "Taking screenshot of " + url

            if VERBOSE:
                print self.getName() + " received argument: " + url
            
            take_screenshot(url, height, width)
            self.queue.task_done() # notify the end of the task


def main():
    global VERBOSE
    global height
    global width

    argparser = argparse.ArgumentParser(description='webshotter - create web page screenshots')
    argparser.add_argument('urllist', help='list with URLs to take screenshots')    # mandatory argument
    argparser.add_argument('-x', '--height', help='height of the headless browser')
    argparser.add_argument('-y', '--width', help='width of the headless browser')
    argparser.add_argument('-t', '--threads', help='number of concurrent threads (default: 1)')
    argparser.add_argument('-v', '--verbose', action='store_true', help='toggle verbose mode')
    args = argparser.parse_args()

    url_list = args.urllist
    num_threads = 1 # default value

    ''' setup threads and their queues '''
    if args.threads and int(args.threads) > 0:
        num_threads = int(args.threads)
    if args.verbose:
        VERBOSE = True
    
    if VERBOSE:
        print "Starting with " + str(num_threads) + " threads"
    for n in range(num_threads):
        if args.height and args.width and int(args.height) > 0 and int(args.width) > 0:
            height = int(args.height)
            width = int(args.width)
            
        t = ThreadScreenshotter(queue)
        t.setDaemon(True)
        t.start()

    try:
	    fd = open(url_list, "r")
    except IOError as err:
    	print "Error opening URL list: %s" % str(err)
    	sys.exit(0)

    urls = fd.read().splitlines()

    ''' reads URLs from file and put them in a queue to be used by the threads '''
    for url in urls:
        if not url.startswith("http"):
            url = "http://" + url
        queue.put(url)
    
    queue.join() # wait for the queue to process everything
            

''' Takes screenshot using PhantomJS's webdriver and saves the file on disk
    This function gets called by the threaded screenshot class
'''
def take_screenshot(url, height, width):
    date_hour = get_date_hour()
    save_file = url + '-screenshot-' + date_hour + '.png'
    save_file = parse_filename(save_file)

    try:
        driver = webdriver.PhantomJS()
        if height > 0 and width > 0:
            driver.set_window_size(height, width)
        driver.get(url)
    	driver.save_screenshot(save_file)
    	driver.quit()
    except WebDriverException as e:
        print "Error in PhantomJS: " + str(e)


''' Returns date and hour in a friendly format for the filename '''
def get_date_hour():
    date_hour = str(datetime.datetime.now())
    date_hour = date_hour.replace(" ", "_").replace(":","")
    
    # remove miliseconds
    i = date_hour.find(".") 
    if i > 0:
	date_hour = date_hour[:i]
        return date_hour


''' This function sanitizes the URL to a filename to be saved in the filesystem '''
def parse_filename(url):
    return url.replace(":", "_").replace("/","_")


if __name__ == "__main__":
	main()

