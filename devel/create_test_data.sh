#!/bin/sh
echo "-> Listing dtool datasets"
dtool ls s3://test-bucket

# Add datasets if there are less than two in the system
cd /tmp

echo "-> Creating test dataset 1"
rm -rf test_dataset_1
dtool create test_dataset_1
cat << EOF > test_dataset_1/README.yml
---
key1: "value1"
key2: 2.3
EOF
curl -k https://creativecommons.org/publicdomain/zero/1.0/legalcode.txt > test_dataset_1/data/test_data.txt
dtool freeze test_dataset_1
dtool cp test_dataset_1 s3://test-bucket
#rm -rf test_dataset_1

echo "-> Creating test dataset 2"
rm -rf test_dataset_2
dtool create test_dataset_2
cat << EOF > test_dataset_2/README.yml
---
key1: "value3"
key2: 42
EOF
curl -k https://creativecommons.org/licenses/by-nc/4.0/legalcode.txt > test_dataset_2/data/i_am_a_text_file.txt
dtool freeze test_dataset_2
dtool cp test_dataset_2 s3://test-bucket
#rm -rf test_dataset_2

echo "-> Listing dtool datasets"
dtool ls s3://test-bucket
