# Vulnerable application for testing automated testers
### So far contains:
- Registering users, logging in
- Password hashing (no salt, free to choose hash function from python's hashlib)
- Acess user's cpr by their username in the url (/home/<username>)
- Cookies: not HttpOnly, not Secure, no extra settings
- Verbose errors when accessing home/username/cpr, where username.cpr != cpr
- 
