#!/bin/sh
echo "-> Creating keys..."
openssl genrsa -out /keys/jwt_key 2048
openssl rsa -in /keys/jwt_key -pubout -outform PEM -out /keys/jwt_key.pub

python3 -m pip install -e .

echo "-> Listing dtool datasets"
dtool ls s3://test-bucket

# Add datasets if there are less than two in the system
if [ $(dtool ls s3://test-bucket | wc -l) -lt "4" ]; then
    cd /tmp

    echo "-> Creating test dataset 1"
    rm -rf test_dataset_1
    dtool create test_dataset_1
    echo <<EOF > test_dataset_1/README.yml
    ---
    key1: "value1"
    key2: 2.3
EOF
    curl -k https://creativecommons.org/publicdomain/zero/1.0/legalcode.txt > test_dataset_1/data/test_data.txt
    dtool freeze test_dataset_1
    dtool cp test_dataset_1 s3://test-bucket
    rm -rf test_dataset_1

    echo "-> Creating test dataset 2"
    rm -rf test_dataset_2
    dtool create test_dataset_2
    echo <<EOF > test_dataset_2/README.yml
    ---
    key1: "value3"
    key2: 42
EOF
    curl -k https://creativecommons.org/licenses/by-nc/4.0/legalcode.txt > test_dataset_2/data/i_am_a_text_file.txt
    dtool freeze test_dataset_2
    dtool cp test_dataset_2 s3://test-bucket
    rm -rf test_dataset_2

    echo "-> Listing dtool datasets"
    dtool ls s3://test-bucket

    cd /app
fi

if [ ! -d migrations ]; then
    echo "-> Initialize database..."
    flask db init
fi

echo "-> Migrating database..."
flask db migrate
flask db upgrade

echo "-> Register base URI..."
flask base_uri add s3://test-bucket

echo "-> Creating test user..."
flask user add test-user

echo "-> Setting permissions for test user..."
flask user search_permission test-user s3://test-bucket

echo "-> Index base URI..."
flask base_uri index s3://test-bucket

echo "-> Starting gunicorn..."
exec gunicorn -b :5000 --access-logfile - --error-logfile - --log-level ${LOGLEVEL} wsgi:app
