#!/bin/bash

usage() { echo "Usage: $0 -f <dataset main folder RELATIVE path>" 1>&2; exit 1; }

if [ "$#" -eq 0 ]
then
  usage
  exit 2
fi

while getopts "f:" o; do
    case "${o}" in
        f)
            dataset_folder=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

if [ -z "${dataset_folder}" ]; then
    usage
fi

script_path="$(pwd)"

echo "Converting Lisa dataset from folder ${dataset_folder}"
cd "${dataset_folder}"

echo "Removing zip files"
rm -rf *.zip
echo "Removing sample folders"
rm -rf sample-dayClip6
rm -rf sample-nightClip1
echo "Removing night folders" # to speed up training
rm -rf night*
rm -rf Annotations/night*
echo "Creating folders"
mkdir train2017
mkdir val2017
mkdir annotations

# daySequence1 and nightSequence1 are the testing images
for f in `find . -type f -path '*daySequence1*/*' -name '*jpg'`
do
   echo "Moving ${f} to test folder"
   mv $f val2017
done
for f in `find . -type f -path '*nightSequence1*/*' -name '*jpg'`
do
   echo "Moving ${f} to test folder"
   mv $f val2017
done
# Everything else is for training
for f in `find . -type f -path '*Train*/*' -name '*jpg'`
do
   echo "Moving ${f} to training folder"
   mv $f train2017
done
for f in `find . -type f -path '*Sequence*/*' -name '*jpg'`
do
   echo "Moving ${f} to training folder"
   mv $f train2017
done

echo "Merging all annotations into a single file..."
cd "$script_path"
python3 merge_csv_data.py "${dataset_folder}"
mv training_data.csv "${dataset_folder}"
mv test_data.csv "${dataset_folder}"
python3 csv_data_to_json.py "${dataset_folder}"
mv instances_train2017.json "${dataset_folder}"
mv instances_val2017.json "${dataset_folder}"
cd "${dataset_folder}"
mv training_data.csv test_data.csv \
        instances_train2017.json instances_val2017.json annotations

echo "Removing empty folders..."
rm -rf daySequence*
rm -rf dayTrain
rm -rf nightSequence*
rm -rf nightTrain
rm -rf Annotations

echo 'Finished!'