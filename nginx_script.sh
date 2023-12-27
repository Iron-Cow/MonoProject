#!/bin/sh

echo "Starting Nginx with API_PORT=$PORT_API_HOST"

# Replace the API_PORT placeholder
sed -i "s/\${PORT_API_HOST}/$PORT_API_HOST/g" /etc/nginx/nginx.conf
sed -i "s/\${PORT_FRONTEND}/$PORT_FRONTEND/g" /etc/nginx/nginx.conf
sed -i "s/\${HOSTNAME_BACKEND}/$HOSTNAME_BACKEND/g" /etc/nginx/nginx.conf
sed -i "s/\${HOSTNAME_FRONTEND}/$HOSTNAME_FRONTEND/g" /etc/nginx/nginx.conf
sed -i "s/\${SSL}/$SSL/g" /etc/nginx/nginx.conf

# Start Nginx
nginx -g 'daemon off;'
