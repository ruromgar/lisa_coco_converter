import pandas as pd
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('folder_path', type=str, help='Dataset main folder RELATIVE path')
args = parser.parse_args()
DATASET_PATH = args.folder_path

def get_folders(annotations=False):
    # Getting dataset root path
    dir_path = os.path.dirname(os.path.realpath(__file__))
    lisa_path = os.path.join(dir_path, DATASET_PATH)

    # Image folders names
    # Not selecting night images to speed up training
    #day_train_folders   = [os.path.join('dayTrain', f'dayClip{i}') for i in range(1, 14)]
    #night_train_folders = [os.path.join('nightTrain', f'nightClip{i}') for i in range(1, 6)]
    #train_folders = day_train_folders + night_train_folders + ['daySequence2', 'nightSequence2']
    #test_folders        = ['daySequence1', 'nightSequence1']

    day_train_folders   = [os.path.join('dayTrain', f'dayClip{i}') for i in range(1, 14)]
    train_folders       = day_train_folders + ['daySequence2']
    test_folders        = ['daySequence1']

    if annotations:
        train_folders = [os.path.join(lisa_path, 'Annotations', 'Annotations', i) for i in train_folders]
        test_folders = [os.path.join(lisa_path, 'Annotations', 'Annotations', i) for i in test_folders]
    else:
        train_folders = [os.path.join(lisa_path, i) for i in train_folders]
        test_folders = [os.path.join(lisa_path, i) for i in test_folders]

    return train_folders, test_folders


def get_full_csv():
    columns = ['Filename', 'Annotation tag', 'Upper left corner X', 'Upper left corner Y', 'Lower right corner X', 
        'Lower right corner Y', 'Origin file', 'Origin frame number', 'Origin track', 'Origin track frame number']
    train_df = pd.DataFrame(columns=columns)
    test_df = pd.DataFrame(columns=columns)

    train_folders, test_folders = get_folders(annotations=True)

    for f in train_folders:
        new_df = pd.read_csv(os.path.join(f, 'frameAnnotationsBOX.csv'), sep=';')
        print(f'Processing {os.path.join(f, "frameAnnotationsBOX.csv")} training file with {new_df.shape[0]} rows.')
        train_df = train_df.merge(new_df, how='outer', left_on=columns, right_on=columns)

    train_df.to_csv('training_data.csv', index=False)
    print(f'Finished processing {train_df.shape[0]} rows')

    for f in test_folders:
        new_df = pd.read_csv(os.path.join(f, 'frameAnnotationsBOX.csv'), sep=';')
        print(f'Processing {os.path.join(f, "frameAnnotationsBOX.csv")} test file with {new_df.shape[0]} rows.')
        test_df = test_df.merge(new_df, how='outer', left_on=columns, right_on=columns)

    test_df.to_csv('test_data.csv', index=False)
    print(f'Finished processing {test_df.shape[0]} rows')

get_full_csv()