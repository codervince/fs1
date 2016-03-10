Flatstats.co.uk Middleware
=======
Scrapy middleware that grabs reports from links like https://www.flatstats.co.uk/racing-system-builder.php?snapshot_id=XXXXX
It intercepts these URLs, fetches data using Selenium and return HtmlResponse object with scraped data as response body back to the spider.

Settings
-------
`settings.py` contains following settings for middleware:

* `FLATSTATS_LOGIN = '<username>'` - flatstats.co.uk username

* `FLATSTATS_PASSWORD = '<password>'` - flatstats.co.uk password
    
* `FLATSTATS_DRIVER = 'Firefox'` - Selenium webdriver to use (http://selenium-python.readthedocs.org/api.html). Available values are:

    - Firefox
    - Chrome
    - Ie
    - Opera
    - PhantomJS
    
Tested on `Firefox` under OSX.

To enable middleware add it to `DOWNLOADER_MIDDLEWARES` section, i.e.:

    DOWNLOADER_MIDDLEWARES = {
       'flatstats.middlewares.FlatstatsMiddleware': 543,
    }

Using middleware
-------
When enabled middleware intercepts requests with URLs containing `www.flatstats.co.uk/racing-system-builder.php` and processes
it using Selenium webdriver. It returns then `Response` object containing HTML with three `div` elements:

* `<div id="full-report">` - summary report (the one got on __Full SP__ button click)
* `<div id="runners">` - runners report (from __Runners__ button)
* `<div id="contenders">` - contenders report (from __Contenders__ button)
# fs1