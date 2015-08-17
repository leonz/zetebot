A simple chat bot for Slack using the real time messaging API, written in Python.  Features are based on those from Hubot by GitHub.

Zetebot's general framework is defined in zetebot.py.  It's features are
implemented via handlers, which are stored in the /handler folder. The scheduler
is run independently from Zetebot in a separate process via cron.

A handler requires two functions: identify and handle.  Identify returns a boolean
if the input message matches the criteria for the handler, i.e., if that handler
should act on the message.  Handle performs the work and returns a response
message.

To add a new feature, add the handler to the /handle folder, import the handler
in the /handle/\_\_init\_\_.py file, and add a condition to Zetebot's
map\_message\_to\_handler function.  I'm looking to simplify this process.

To add a handler, create a new handle file in the /handle folder
