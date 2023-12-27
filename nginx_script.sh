#!/bin/sh

echo "Starting Nginx with PORT_ENTRY_NGINX=$PORT_ENTRY_NGINX"
echo "Starting Nginx with PORT_API_CONTAINER=$PORT_API_CONTAINER"
echo "Starting Nginx with HOSTNAME_BACKEND=$HOSTNAME_BACKEND"
echo "Starting Nginx with HOSTNAME_FRONTEND=$HOSTNAME_FRONTEND"

# Replace the API_PORT placeholder
sed -i "s/\${PORT_API_CONTAINER}/$PORT_API_CONTAINER/g" /etc/nginx/nginx.conf
sed -i "s/\${PORT_FRONTEND}/$PORT_FRONTEND/g" /etc/nginx/nginx.conf
sed -i "s/\${HOSTNAME_BACKEND}/$HOSTNAME_BACKEND/g" /etc/nginx/nginx.conf
sed -i "s/\${HOSTNAME_FRONTEND}/$HOSTNAME_FRONTEND/g" /etc/nginx/nginx.conf
sed -i "s/\${SSL}/$SSL/g" /etc/nginx/nginx.conf

# Start Nginx
nginx -g 'daemon off;'
