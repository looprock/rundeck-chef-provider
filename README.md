rundeck-chef-provider
=====================

A simple python based rundeck provider generated from chef, using pychef, which outputs to a file.  This file should be served as a static resource by something like apache or nginx.

I had multiple issues using some other providers I won't name, so I decided to write my own. We were already doing a curl and caching output as the providers we were using were too slow to be that useful given the number of nodes we were managing, so this was an easy fix.
