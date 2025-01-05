import os
import random
import shutil

data_path = './car'
train_path = './train'
valid_path = './valid'

if os.path.exists(train_path):
    shutil.rmtree(train_path)
if os.path.exists(valid_path):
    shutil.rmtree(valid_path)

os.makedirs(os.path.join(train_path, 'images'))
os.makedirs(os.path.join(train_path, 'labels'))
os.makedirs(os.path.join(valid_path, 'images'))
os.makedirs(os.path.join(valid_path, 'labels'))

files = [os.path.splitext(file)[0] for file in os.listdir(os.path.join(data_path, "images"))]
random.shuffle(files)
mid = int(len(files) * 0.8)

def copy_file_with_ext(src_dir, dest_dir, file_name, extensions):
    for ext in extensions:
        src = os.path.join(src_dir, f'{file_name}{ext}')
        dest = os.path.join(dest_dir, f'{file_name}{ext}')
        if os.path.exists(src):
            shutil.copy(src, dest)
            print(f"Copied: {src} -> {dest}")
            return True
    print(f"File not found: {file_name}")
    return False

# Copy training files
for file in files[:mid]:
    # Images
    copy_file_with_ext(os.path.join(data_path, "images"),
                       os.path.join(train_path, "images"),
                       file, ['.jpg', '.png'])
    # Labels
    copy_file_with_ext(os.path.join(data_path, "labels"),
                       os.path.join(train_path, "labels"),
                       file, ['.txt'])

# Copy validation files
for file in files[mid:]:
    # Images
    copy_file_with_ext(os.path.join(data_path, "images"),
                       os.path.join(valid_path, "images"),
                       file, ['.jpg', '.png'])
    # Labels
    copy_file_with_ext(os.path.join(data_path, "labels"),
                       os.path.join(valid_path, "labels"),
                       file, ['.txt'])
