import cv2
from imaging_interview import preprocess_image_change_detection, compare_frames_change_detection

# higher kernel size results lower difference score
# lower difference score means more similar images

# adjust: gaussian blur kernel, min contour area parameters

def similarity_test():

    image1_path = 'data_samples/image1_1.png'
    image2_path = 'data_samples/image1_2.png'
    
    image1 = cv2.imread(image1_path)
    image2 = cv2.imread(image2_path)
    
    # check if image read is successfull
    if image1 is None or image2 is None:
        print("Image loading error.")
        return
    
    # enable/disable showing images
    show_images = True
    
    # define GaussianBlur radius list parameter, adjust and see results
    gaussian_blur_kernel = [15] # higher kernel size results lower difference score
    
    # preprocess images
    image1_preprocessed = preprocess_image_change_detection(image1, gaussian_blur_kernel)
    image2_preprocessed = preprocess_image_change_detection(image2, gaussian_blur_kernel)

    # define min_contour_area parameter, adjust and see the score
    contour_area = 5000
    
    # compare previous and next frames
    # lower difference score means more similar images
    difference_score, _, _ = compare_frames_change_detection(image1_preprocessed, image2_preprocessed, contour_area)
    print("Difference Score: ", difference_score)

    if show_images:
        # display images in separate windows
        cv2.imshow('Image 1', image1)
        cv2.imshow('Image 2', image2)
        cv2.imshow('Preprocessed Image 1', image1_preprocessed)
        cv2.imshow('Preprocessed Image 2', image2_preprocessed)

        # press 'q' to exit
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

        # close windows
        cv2.destroyAllWindows()

if __name__ == "__main__":
    similarity_test()