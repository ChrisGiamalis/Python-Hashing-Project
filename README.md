This project investigates the security and performance implications of iterative password hashing 
using salted SHA‑256. By varying the number of hash iterations from a single application to 
millions, the experiment measures median latency, attacker throughput, and slowdown factors 
relative to a baseline. Results demonstrate that increasing iterations proportionally reduces the 
number of guesses an attacker can perform per second, thereby strengthening resistance to 
brute‑force attacks. At the same time, the experiment highlights the tradeoff between enhanced 
security and acceptable login latency for legitimate users. While iterative SHA‑256 is not 
recommended for production systems, the study provides a reproducible framework for 
understanding how iteration counts influence attacker cost and serves as a foundation for 
comparing modern password‑based key derivation functions such as PBKDF2, bcrypt, and 
Argon2.
