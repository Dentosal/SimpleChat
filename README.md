# SimpleChat
A simple but secure chat service with web frontend.

## Hosting an instance
See [SETUP.md](SETUP.md) for details.

## Technology summary
Backend is written using Python 3 and Flask. For production usage, nginx and uwsgi are recommended. Redis is used to store persistent data on backend.
Frontend is written in JavaScript and jQuery.

## Possible improvements
* DoS prevention
* End-to-end encryption for messages, preferably PKI
* Change and reset password
* Loading older messages lazily
* Client-side caching
* No-javascript mode
* Support older browsers (Even IE 11 isn't supported)
* Properly support devices with less than 500px width
* Properly support mobile devices
* User settings for theme/locale/whatever
* Markdown support for messages
* Images, smileys, etc
* Deleting chats and leaving channels
* Keyboard shortcuts
* Automated tests
* Using REST API instead of the current stateful one would be cool
