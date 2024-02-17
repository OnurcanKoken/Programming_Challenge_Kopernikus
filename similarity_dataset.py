import os
import cv2
import time 
import yaml
import argparse
from imaging_interview import preprocess_image_change_detection, compare_frames_change_detection


def group_by_camera_numbers(image_list):
    """
    Group image file names by camera numbers, store in a dictionary
    
    :param image_list: A list of image file names in the given dataset path

    Two image file naming formats are possible: 
    "c%camera_id%-%timestamp%.png" or "c%camera_id%_%timestamp%.png

    Assumption: If the format is "c%camera_id%_%timestamp%.png",
    it should not contain "-" in the "timestamp"

    Return: A dictionary, camera_id as a key and list of image file names for each camera_id as a value
    """
    camera_groups = {}
    for image_file in image_list:
        camera_id = image_file.split('-')[0] if '-' in image_file else image_file.split('_')[0]
        camera_groups.setdefault(camera_id, []).append(image_file)
    return camera_groups

def size_check(img1, img2):
    """
    Check sizes of images before comparison

    :param img1: Current image, single channel
    :param img2: Next image, single channel

    Return: Two images with the same image size
    """
    # get height and width
    h1, w1 = img1.shape # current image
    h2, w2 = img2.shape # next image

    if h1 == h2 and w1 == w2:
        # image sizes are the same
        return img1, img2
    else:
        print("Image sizes are different, resizing the big image.")
        # current frame is smaller
        if h1 < h2:
            img2 = cv2.resize(img2, (w1, h1), interpolation=cv2.INTER_AREA)
        # next frame is smaller
        else:
            img1 = cv2.resize(img1, (w2, h2), interpolation=cv2.INTER_AREA)
        return img1, img2

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

    camera_groups = group_by_camera_numbers(image_file_list)

    # count non-essential frames
    number_of_removed_images = 0
 
    # iterate over each camera_id
    for camera_id, camera_img_list in camera_groups.items():
        # number of images for the corresponding camera_id
        camera_num_images = len(camera_img_list)
        i = 0 # counter for current frame, start comparing with the first frame
        while i < camera_num_images:
            current_frame_path = os.path.join(dataset_path, camera_img_list[i])
            current_frame = cv2.imread(current_frame_path)
            if current_frame is None:
                print("Image reading error:", current_frame_path)
                i += 1
                continue

            current_frame = preprocess_image_change_detection(current_frame, gaussian_blur_kernel)
            j = i + 1 # start comparing with the frame after current_frame
            # compare the current frame with next frames
            while j < camera_num_images:
                next_frame_path = os.path.join(dataset_path, camera_img_list[j])
                next_frame = cv2.imread(next_frame_path)
                if next_frame is None:
                    print("Image reading error:", next_frame_path)
                    j += 1
                    continue

                next_frame = preprocess_image_change_detection(next_frame, gaussian_blur_kernel)
                # check sizes of two images
                current_frame, next_frame = size_check(current_frame, next_frame)
                # compare current frame and next frame
                difference_score, _, _  = compare_frames_change_detection(current_frame, next_frame, min_contour_area)

                # compare the score with the threshold
                if difference_score > similarity_threshold: # images are different
                    j += 1
                else: # images are similar, remove the next_frame
                    print("Removing", camera_img_list[j])
                    camera_img_list.pop(j)
                    os.remove(next_frame_path)
                    camera_num_images -= 1
                    number_of_removed_images += 1
            i += 1
    print("\nNumber of removed images:", number_of_removed_images)

    end_time = time.time()
    duration = end_time - start_time
    print("Processing time:", duration, "seconds")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Compare images in a dataset and remove similar (duplicated) images.")
    parser.add_argument("--dataset_path", type=str, nargs='?', default="dataset")
    args = parser.parse_args()

    # configuration, adjustable parameters
    with open('config.yaml', 'r') as config_file:
        config = yaml.safe_load(config_file)
    similarity_threshold = config.get("similarity_threshold", 5000)
    min_contour_area = config.get("min_contour_area", 1000)
    gaussian_blur_kernel = config.get("gaussian_blur_kernel", [15])

    similarity_over_dataset(args.dataset_path, similarity_threshold, min_contour_area, gaussian_blur_kernel)