import os
import cv2
import time 
import yaml
import argparse
from imaging_interview import preprocess_image_change_detection, compare_frames_change_detection


def group_by_camera_numbers(image_list, dataset_path, gaussian_blur_kernel):
    """
    Group image file names by camera numbers, store images in a dictionary to avoid reading images multiple times
    
    :param image_list: A list of image file names in the given dataset path

    Two image file naming formats are possible: 
    "c%camera_id%-%timestamp%.png" or "c%camera_id%_%timestamp%.png

    Assumption: If the format is "c%camera_id%_%timestamp%.png",
    it should not contain "-" in the "timestamp"

    Return: A nested dictionary, camera_id as a key and dictionary of image file names for each camera_id as a value
    """
    camera_groups = {}
    for image_file in image_list:
        camera_id = image_file.split('-')[0] if '-' in image_file else image_file.split('_')[0]
        image = cv2.imread(os.path.join(dataset_path, image_file))
        if image is None:
                print("Image reading error:", image_file)
                continue
        image = cv2.resize(image, (640, 480), interpolation=cv2.INTER_AREA)
        image = preprocess_image_change_detection(image, gaussian_blur_kernel)

        # check if camera_id key is already exist
        if camera_id in camera_groups:
            camera_groups[camera_id][image_file] = image
        else:
            camera_groups[camera_id] = {image_file : image}
        
    return camera_groups

def similarity_over_dataset(dataset_path, similarity_threshold, min_contour_area, gaussian_blur_kernel):
    """
    Check similarity of images and remove duplicated or almost duplicated images
    
    :param dataset_path: The path to a folder with images, the dataset directory
    :param similarity_threshold: Threshold to decide if images are similar or different
    :param min_contour_area: Threshold to filter small differences between two images
    :param gaussian_blur_kernel: Kernel size to apply Gaussian blur filter
    """
    start_time = time.time()

    # read images with .png format and sort
    image_file_list = [f for f in os.listdir(dataset_path) if f.endswith(('.png'))]
    image_file_list.sort() 

    camera_groups = group_by_camera_numbers(image_file_list, dataset_path, gaussian_blur_kernel)

    # count non-essential frames
    number_of_removed_images = 0
    # iterate over each camera_id
    for camera_id, camera_img_dict in camera_groups.items():
        # iterate over each image_file for the corresponding camera_id
        for image_file, current_frame in list(camera_img_dict.items()):
            if current_frame is None:
                continue
            # this part still can be improved
            for image_file_2, next_frame in list(camera_img_dict.items()):
                if image_file == image_file_2 or next_frame is None:
                    continue
                # compare current frame and next frame
                difference_score, _, _  = compare_frames_change_detection(current_frame, next_frame, min_contour_area)
                # compare the score with the threshold
                if difference_score > similarity_threshold: # images are different
                    continue
                else: # images are similar, remove the next_frame
                    print("Removing", image_file_2)

                    camera_img_dict.update({image_file_2:None})
                    os.remove(os.path.join(dataset_path, image_file_2))
                    number_of_removed_images += 1

    print("\nNumber of removed images:", number_of_removed_images)

    end_time = time.time()
    duration = end_time - start_time
    print("Processing time:", duration, "seconds")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Compare images in a dataset and remove similar (duplicated) images.")
    parser.add_argument("--dataset_path", type=str, default="dataset")
    args = parser.parse_args()

    # configuration, adjustable parameters
    with open('config.yaml', 'r') as config_file:
        config = yaml.safe_load(config_file)
    similarity_threshold = config.get("similarity_threshold", 500)
    min_contour_area = config.get("min_contour_area", 100)
    gaussian_blur_kernel = config.get("gaussian_blur_kernel", [3,5])

    similarity_over_dataset(args.dataset_path, similarity_threshold, min_contour_area, gaussian_blur_kernel)