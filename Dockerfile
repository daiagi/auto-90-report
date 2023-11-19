# Define custom function directory
ARG FUNCTION_DIR="/function"

FROM python:3.8-slim as build-image

RUN apt-get update && apt-get install -y wget unzip

# Install Chromedriver
# Specify the Chromedriver version
ARG CHROMEDRIVER_URL=https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/linux64/chromedriver-linux64.zip

# Download and Install Chromedriver
RUN wget -q -O /tmp/chromedriver_linux64.zip $CHROMEDRIVER_URL && \
    unzip -qq /tmp/chromedriver_linux64.zip -d /opt/chromedriver && \
    rm /tmp/chromedriver_linux64.zip

# Make Chromedriver executable
RUN chmod +x /opt/chromedriver/chromedriver-linux64/chromedriver

# Include global arg in this stage of the build
ARG FUNCTION_DIR

# Copy function code
RUN mkdir -p ${FUNCTION_DIR}
COPY . ${FUNCTION_DIR}

# Install the function's dependencies
RUN pip install -r ${FUNCTION_DIR}/requirements.txt --target ${FUNCTION_DIR}


# Use a slim version of the base Python image to reduce the final image size
FROM python:3.8-slim

# Install system dependencies required for Chrome and Chromedriver
RUN apt-get update && apt-get install -y wget

# Install Google Chrome
ENV CHROME_VERSION=119.0.6045.105-1
RUN wget -q https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb
RUN apt-get install -y ./google-chrome-stable_${CHROME_VERSION}_amd64.deb

# Create a symbolic link to Chromedriver
RUN ln -fs /opt/chromedriver/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

# Copy in the built dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}
COPY --from=build-image /opt/chromedriver/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver

# Set runtime interface client as default command for the container runtime
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
# Pass the name of the function handler as an argument to the runtime
CMD [ "lambda_function.handler" ]