import json
import os
from matplotlib import pyplot as plt
import matplotlib.patches as patches
import random

def get_category(i, categories):
    '''
    IN: 
        -i: int of 'category_id' you would like identified
        -categories: 'categories' section of coco json
    OUT: 
        -name of object category, or "none" if the category isn't present
    '''
    for c in categories:
        if c['id'] == i:
            return c['name']
    return "None"
        
def get_category_counts(json_path):
    '''
    IN: json_path: path to coco json gt file
    OUT: dict of form {category name: count of objects}
    '''
    # Open json file
    with open(json_path, 'r') as f:
        contents = json.load(f)
    
    # Pull out key sections
    anns = contents['annotations']
    cats = contents['categories']

    # Create dictionary of by-class counts
    cat_counts = {}
    for a in anns:
        cat = a['category_id']
        name = get_category(cat, cats)
        if name not in cat_counts:
            cat_counts[name] = 1
        else:
            cat_counts[name] = cat_counts[name] + 1
    
    return cat_counts


def json_fewer_cats(old_json, cat_list, ims_no_anns = False):
    '''
    PURPOSE: Create a json with a subset of object categories
    IN:
        -old_json: gt coco json
        -cat_list: list of int category ids to be included in new coco gt json
        -ims_no_anns: if False (default), remove images without annotations from 'images', else keep all original images
    OUT: (new_name) path to new json file 
    '''
    # Name new json by the number of categories being included
    new_name = old_json.replace('.', '_{}.'.format(len(cat_list)))
    
    # Open original gt json
    with open(old_json, 'r') as f:
        contents = json.load(f)
        
    # Pull out key sections of old gt 
    annotations = contents['annotations']
    images = contents['images']
    
    # Create new json, with blank annotations
    new_json = contents.copy()
    new_json['annotations'] = []
    
    # Feedback
    print(len(annotations), 'annotations found')
    
    # Process annotations, keeping only those which are in the desired categories
    count = 0
    for a in annotations:
        cat_id = a['category_id']
        if cat_id in cat_list:
            new_json['annotations'].append(a)
        count += 1
    
    # If desired, only keep images that have annotations on them
    if not ims_no_anns:
        new_json['images'] = []
        print(len(images), "images in original data")
        # Check each image for annotations
        for i in images:
            anns = []
            im_id = i['id']
            for a in new_json['annotations']:
                if a['image_id'] == im_id:
                    anns.append(a)
            if len(anns) > 1:
                new_json['images'].append(i)
        print(len(new_json['images']), "images in new data")
    
    # Feedback
    print(len(new_json['annotations']), 'annotations in new file at', new_name)
    
    # Ensure no .json funny business will happen
    if os.path.exists(new_name):
        os.remove(new_name)
    
    # Save new file
    with open(new_name, 'w') as f:
        json.dump(new_json, f)
    
    return new_name

def anns_on_image(im_id, json_path):
    '''
    IN: 
        - im_id: int id for 'id' in 'images' of coco json
        - json_path: path to coco gt json
    OUT:
        - on_image: list of annotations on the given image
    '''
    # Open json
    with open(json_path, 'r') as f:
        contents = json.load(f)
    
    # Pull out annotations
    anns = contents['annotations']
    
    # Create list of anns on this image
    on_image = []
    for a in anns:
        if a['image_id'] == im_id:
            on_image.append(a)
    
    return on_image

def choose_random_ims(num_ims, json_path):
    '''
    IN:
        -num_ims: int number of image ids desired
        -json_path: path to gt coco json
    OUT:
        -list of num_ims random image ids from the input json
    '''
    # Open json
    with open(json_path, 'r') as f:
        contents = json.load(f)
    
    # Pull out key section
    images = contents['images']
    
    # Get a list of all image ids in the json
    all_ims = []
    for i in images:
        all_ims.append(i['id'])
    
    # Enusre there are no duplicates in the list
    all_ims = list(set(all_ims))
    
    # Shuffle the list
    random.shuffle(all_ims)
    
    # Create a smaller list of the num_ims requested
    rand_ims = all_ims[:num_ims]
    
    return rand_ims

def display_random_ims(num_ims, json_path, image_folder):
    '''
    PURPOSE: Display some number of images from a coco dataset, randomly selected
    IN:
        -num_ims: int indicating how many to display
        -json_path: coco gt file
        -image_folder: folder where images in json_path are located
    OUT:
        -figures with each randomly selected image and its annotations
    '''
    # Pick the image ids to display
    ims = choose_random_ims(num_ims, json_path)
    
    # Process each image
    for i in ims:
        # Get annotations on this image
        anns = anns_on_image(i, json_path)
        
        # Display the image
        im_path = image_folder + str(i) + '.tif'
        plt.figure()
        f,ax = plt.subplots(1, figsize = (30,30))
        img = plt.imread(im_path)
        plt.imshow(img)
        
        # Add boxes for each annotation
        for a in anns:
            b = a['bbox']
            rect = patches.Rectangle((b[0], b[1]), b[2], b[3], edgecolor = 'r', facecolor = "none")
            ax.add_patch(rect)
        plt.show()
    
    return