Shadow Scanner V1.0

This port scanner will probe a single IP address using SYN packets in search for services.
Assuming said ports running a service aren't closed/filtered, the scanner will receive a
SYN/ACK packet which will confirm the existence of an open port/valid service. Only open
ports will be verbose to the user.

This scanner accepts single port entrys of from an entire range, ex: "1-2014"
Ranges are seperated by a hyphen.

It is known as a 'SYN Stealth' scan since it is less noisy on the network than to use
the standard TCP-connection scan, and fully establish a socket. Connect method can
actually lead to TCP socket exhaustion altogether as probing ports too quickly will
put the sockets in a TIME_WAIT status for up to 60 seconds.

This scanner makes use a wait (sleep in milliseconds) after each SYN probe is sent.
This also allows the tool to work more quietly and be less aggressive when checking
ports.
