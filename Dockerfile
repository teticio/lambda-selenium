FROM public.ecr.aws/lambda/python:3.11

# Install Chrome for testing
RUN yum update -y &&  \
    yum install -y alsa-lib atk at-spi2-atk at-spi2-core bash ca-certificates cairo chkconfig curl expat glib2 glibc gtk3 jq libcurl libdrm libgcc libX11 libxcb libXcomposite libXdamage libXext libXfixes libxkbcommon libXrandr mesa-libgbm nspr nss nss-util pango tar unzip vulkan wget xdg-utils && \
    LATEST_CHROME_RELEASE=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | jq '.channels.Stable') && \
    LATEST_CHROME_URL=$(echo "$LATEST_CHROME_RELEASE" | jq -r '.downloads.chrome[] | select(.platform == "linux64") | .url') && \
    wget -N "$LATEST_CHROME_URL" && \
    unzip chrome-linux64.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chrome-linux64/chrome && \
    ln -s /usr/local/bin/chrome-linux64/chrome /usr/bin/google-chrome && \
    rm chrome-linux64.zip 

# Install Selenium
RUN pip install selenium undetected-chromedriver

# Add application code
COPY lambda_function.py /var/task

# Set the CMD to the handler
CMD ["lambda_function.lambda_handler"]
