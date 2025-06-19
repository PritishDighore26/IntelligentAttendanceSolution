# Use the pre-built dlib base image
FROM prafulcoder/py-dlib-base:v-1

# Set the working directory
WORKDIR /opt/project

# Copy essential project files in a single layer to reduce image size
COPY pyproject.toml README.md Makefile ./

# Copy application source code and static files in separate layers for better caching
COPY IAS/ IAS/
COPY staticfiles/ staticfiles/
COPY media/ media/

# Copy the shape predictor model
COPY shape_predictor_68_face_landmarks.dat ./

RUN set -xe \
    && apt-get update \
    && pip install virtualenvwrapper poetry==1.4.2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Optimize Poetry's connection pool for faster installations
RUN poetry config installer.max-workers 20

# Install project dependencies without re-installing dlib
RUN poetry install --no-root --no-interaction --no-ansi -vvv

# Display Poetry environment information
RUN poetry env info

# Expose the application port
EXPOSE 8000

# Set up the entrypoint script
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh

# Define the container's entrypoint
ENTRYPOINT ["/entrypoint.sh"]
