# Use an official Node runtime as a parent image
FROM node:14

# Set the working directory in the container
WORKDIR .

# Copy package.json and package-lock.json
COPY package.json ./
COPY package-lock.json ./

## Define environment variable
#ARG API_HOST
#ARG REACT_APP_DB_NAME
#ENV REACT_APP_DB_NAME=$REACT_APP_DB_NAME
#ENV API_HOST=$API_HOST
#ENV DB_MODE $DB_MODE
#ENV NODE_ENV productionnnn
#ENV NODE_ENV2 productionnnns

# Install any needed packages specified in package.json
RUN npm install

# Bundle app source inside Docker image
COPY . .

# Build the app
RUN npm run build

## Install `serve` to run the application
RUN npm install -g serve

# Make port 3000 available to the world outside this container
EXPOSE 3000


# Run the app when the container launches
#CMD ["serve", "-s", "build", "-l", "3000"]
CMD ["npm", "start"]
