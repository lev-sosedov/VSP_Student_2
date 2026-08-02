# Production server requirements

- Ubuntu LTS with current security updates;
- 2 vCPU / 4 GB RAM minimum, 4 vCPU / 8 GB RAM recommended;
- 40 GB SSD minimum plus backup capacity;
- one public IPv4 and DNS A records for `vsp-student.ru` and `www`;
- firewall: SSH 22 restricted to operators, HTTP 80, HTTPS 443;
- SSH keys only; disable password authentication after key access is verified;
- Docker Engine and the Compose plugin;
- at least 2 GB swap;
- UTC timezone and automatic security updates;
- fail2ban where SSH exposure warrants it.

Keep `/opt/vsp/secrets` and `/opt/vsp/backups` outside Git with restrictive
permissions. Caddy is the only public listener.
