#!/bin/zsh
#
# Check if the local API is running
if ! curl --fail-with-body 0.0.0.0:8080/plugins/nvim-lspconfig; then
    echo "API is not running, starting..."
    # Build & run container
    cd ../nvim-plugin-api/
    docker build . -t nvim-plugin-api && docker run --env-file .env -p 8080:8080 --detach -t nvim-plugin-api /venv/bin/gunicorn -b 0.0.0.0:8080 --access-logfile - --error-logfile - src.main:app
    cd ../nvim-plugin-frontend/
fi


# Run tailwindcss build
cd static/
npx tailwindcss -i ./src/style.css -o css/main.css
cd ../

# Run prettier
prettier -w templates/*
prettier -w static/*

# Start Flask server 
# flask run 

