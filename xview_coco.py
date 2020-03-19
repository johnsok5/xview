import json
import shutil
import os
from matplotlib import pyplot as plt

def get_bbox(feature):
    '''
    IN: feature from xview geojson
    OUT: int bbox of form [x1, y1, w,h]
    '''
    # Pull out xview pixel box, convert all value to integers
    box = feature['properties']['bounds_imcoords'].split(',')
    box = [int(b) for b in box]
    [x1, y1, x2, y2] = box.copy()
    
    # Calculate width, height
    w = x2 - x1
    h = y2 - y1
    
    return [x1, y1, w, h]

def get_bbox_geos(feature):
    '''
    IN: feature from xview geojson
    OUT: float bbox of form [lat1, long1, w,h]
    '''
    
    # Pull out list of geocoordinate points
    coords = feature['geometry']['coordinates']
    
    # Make lists of lats and longs 
    lats = []
    longs = []
    for c in coords[0]:
        lats.append(c[0])
        longs.append(c[1])
    
    # Pull out smallest and largest values
    lat_1 = min(lats)
    lat_2 = max(lats)
    long_1 = min(longs)
    long_2 = max(longs)
    
    # Calculate width, height
    w = lat_2 - lat_1
    h = long_2 - long_1
    
    return [lat_1, long_1, w, h]

def get_images(image_folder):
    '''
    IN: image folder where images you want in your coco .json are stored
    OUT: coco style 'images' section
    '''
    
    images = []
    
    imgs = os.listdir(image_folder)
    
    print("Found {} images in folder".format(len(imgs)))
    count = 0
    
    for i in imgs:
        img = plt.imread(image_folder + i)
        (h, w, c) = img.shape
        
        im_id = int(i.split('.')[0])
        
        image = {
            "id" : im_id,
            "width" : w,
            "height": h,
            "file_name": i,
            "license": 1
        }
        
        images.append(image)
        count += 1
        if count % 50 == 0:
            print(count, "images processed")
        
        
    return images

def get_categories(classes_path):
    '''
    IN: .txt file with xview classes and ids
    OUT: coco gt 'categories' section
    '''
    categories = []
    
    # Open text file
    with open(classes_path, 'r') as f:
        txt = f.readlines()
    txt = [t.replace('\n', '') for t in txt]

    # Add a category for each line in txt file
    for t in txt:
        cat_id = int(t.split(':')[0])
        name = str(t.split(':')[1].replace("'",""))
        category = {
            "supercategory" : "None",
            "name" : name,
            "id" : cat_id
        }
        categories.append(category)
    
    return categories

def get_annotations(geojson_path):
    '''
    IN: xview geojson
    OUT: coco gt 'annotations' section
    '''
    annotations = []
    
    # Open gejson
    with open(geojson_path, 'r') as f:
        xview = json.load(f)
    
    # Pull features section out
    features = xview['features']
    
    # int to assign to each new annotation sequentially
    id_count = 0
    
    # Process each xview feature
    for f in features:
        # Get bounding box, pixels
        bbox = get_bbox(f)
        
        # Calculate area in pixels
        area = bbox[2] * bbox[3]
        
        # Get bbox, geos
        bbox_geos = get_bbox_geos(f)
        
        # Find the id of the category of this annotation
        cat_id = f['properties']['type_id']
        
        # Assign an image id based on the image file name
        im_id = int(f['properties']['image_id'].split('.')[0])
        
        # Populate new annotation and add it to the main variable 
        ann = {
            "id": id_count, 
            "image_id": im_id, 
            "category_id": cat_id, 
            "area": area, 
            "bbox": bbox, 
            "bbox_geos" : bbox_geos,
            "iscrowd": 0  
        }
        annotations.append(ann)
        id_count += 1
    
    return annotations

def make_json(geojson_path, classes_path, image_folder):
    '''
    PURPOSE: translate xview geojson to coco gt file
    IN:
        - geojson_path: path to xview geojson
        - classes_path: path to .txt file with xview class nums/names
        - image_folder: folder of images for these annotations
    OUT: path to new coco json
    '''
    # Open geojson
    with open(geojson_path, 'r') as f:
        xview = json.load(f)
    
    # Create new path to save to
    new_path = geojson_path.replace('.geojson', '.json')
    
    # Populate main 5 coco json fields
    # First 2 are simple, so no function
    licenses = [{"id": 1, "name": "xView"}]
    info = {"year": '2018', "version": '1', "description": 'xView', "contributor": 'DIUx', "date_created": "03/17/2020"}
    # Refer to functions above
    images = get_images(image_folder)
    categories = get_categories(classes_path)
    annotations = get_annotations(geojson_path)
    
    # Create final structure 
    coco_json = {
        'info' : info,
        'licenses' : licenses,
        'images' : images,
        'categories' : categories,
        'annotations' : annotations
    }
    
    # Ensure no funny business with save
    if os.path.exists(new_path):
        os.remove(new_path)
    
    # Save file
    with open(new_path, 'w') as f:
        json.dump(coco_json, f)
    
    # Feedback
    print('New json', new_path)
    
    return new_path