# nginx Load balancer

Links:
- https://upcloud.com/resources/tutorials/configure-load-balancing-nginx
- https://www.nginx.com/blog/using-free-ssltls-certificates-from-lets-encrypt-with-nginx/

```
sudo apt-get update
sudo apt-get install nginx certbot python3-certbot-nginx
sudo ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/vhost

sudo certbot --nginx -d ncar.nationalsciencedatafabric.org

sudo systemctl restart nginx

# check syntax of more /etc/nginx/nginx.conf 
sudo nginx -t 

# check the logs
sudo tail -f /var/log/nginx/*.log

sudo nginx -s stop
sudo nginx -s start
sudo nginx -s reload
```

# Setup site file

This is the body of  `/etc/nginx/sites-available/default`

```
server {

	server_name ncar.nationalsciencedatafabric.org;

	listen 443 ssl default_server;
	listen [::]:443 ssl default_server;
	ssl_certificate /etc/letsencrypt/live/ncar.nationalsciencedatafabric.org/fullchain.pem; # managed by Certbot
	ssl_certificate_key /etc/letsencrypt/live/ncar.nationalsciencedatafabric.org/privkey.pem; # managed by Certbot

	root /var/www/html;

	index index.html index.htm index.nginx-debian.html;

    location / {
        proxy_pass http://127.0.0.1:10787/neon_dashboard/;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_http_version 1.1;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host:$server_port;
        proxy_buffering off;
    }	
    location /neon-demo/v1/ {
        proxy_pass http://127.0.0.1:10787/neon_dashboard/;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_http_version 1.1;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host:$server_port;
        proxy_buffering off;
    }
}
server {
    if ($host = ncar.nationalsciencedatafabric.org) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


	server_name ncar.nationalsciencedatafabric.org;

	listen 80 default_server;
	listen [::]:80 default_server;
    return 404; # managed by Certbot
}
```

# Crontab

```
$ crontab -e
0 12 * * * /usr/bin/certbot renew --quiet

```

# Screen

```
screen -ls 
#         2230870.ncar-session    (07/28/23 21:55:59)     (Detached)


screen -r 2230870.ncar-session

bokeh serve \
  --port=10787 \
  --log-level=debug \
  --allow-websocket-origin=* \
  --address=0.0.0.0 \
  --use-xheaders \
  neon_dashboard
```