#!/bin/sh

echo "Starting Nginx with API_PORT=$API_PORT"

# Replace the API_PORT placeholder
sed -i "s/\${API_PORT}/$API_PORT/g" /etc/nginx/nginx.conf
sed -i "s/\${SSL}/$SSL/g" /etc/nginx/nginx.conf

# Start Nginx
nginx -g 'daemon off;'
