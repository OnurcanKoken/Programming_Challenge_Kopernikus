# Programming_Challenge_Kopernikus
This repository is created to present my solution for the programming challenge of Kopernikus, Perception team.

# Overview

**Task:** Write a program that will find and remove all similar-looking images in a folder.

**Input:** A path to a folder with images.

**Result:** Remove all non-essential for data collection images.

Non-essential: Duplicated or almost duplicated images that have only 
minor differences from the original that may be considered as non-essential.

**Given:** `imaging_interview.py`, contains functions for image comparison.

**Rules:** Use only provided functions for image comparison, there is no need to develop your own comparison algorithm.

**Evaluation:** How you write the program to clean the data, not the algorithm you will use.

# Questions and Answers

## 1. What did you learn after looking on our dataset?

* The dataset contains hours of data collected for days from several cameras that are strategically positioned in the area.
* It is significant to extract only essential frames from a video stream and ensure that each image is unique for perception tasks.
* The dataset may contain images with different resolutions from several cameras, and there might be some broken images. It is important for the script to handle those issues and avoid crashing.
* I guess, ArUco Markers are used in the field for indoor localization. 

## 2. How does your program work?

**Installation:**

- Clone the repository.

```commandline
git clone https://github.com/OnurcanKoken/Programming_Challenge_Kopernikus.git
```

- Create and activate a virtual environment. You can use your preferred method to create a virtual environment such as `venv`, `virtualenv` or `conda`.

- Install dependencies, it is tested with Python 3.9.6.

```commandline
pip install -r requirements.txt
```

- Run the script. By default, the `dataset_path` parameter is set to the `dataset` folder located in the same directory as the Python script (`similarity_dataset.py`). If your dataset folder is located elsewhere, provide the path instead of `dataset`.

```commandline
python similarity_dataset.py --dataset_path dataset
```

**The algorithm of the program:**

* Firstly, it reads all .png images in the given path, then separates by `camera_id` key and stores image file names in lists. 
* For each list of `camera_id`, first frame is picked as `current_frame`, and compared with the following frames (`next_frame`) in the list. 
* To avoid any crush, when image reading fails, it gives an error and continues to compare with the following frames. 
* Preprocess images, apply Gaussian Blur filter and color mask.
* Sizes of images are checked, and the bigger image is resized before the comparison.
* Two images are compared. If the score is smaller than the threshold, `next_frame` is removed from the dataset, otherwise, update the `next_frame` with the following frame until the end of the list.
* Then go back to update `current_frame` and keep comparing with the following frames in the list.
* The algorithm terminates when there is no frame left in each list of `camera_id`.

## 3. What values did you decide to use for input parameters and how did you find these values?

I used `similarity_first_test.py` file, in the test folder, to make it easier to tune the parameters and observe the changes. Later, I created a `config.yaml` file to make it easier to adjust parameters for the actual solution, `similarity_dataset.py` file.

* **gaussian_blur_kernel:** At first, I started testing with 3x3 kernel size and checked how blurry images become. I decided to increase the size by setting the parameter to [3, 5], and [5, 7] where it applies the filter twice. I kept the parameter **min_contour_area** as zero and checked how **difference_score** variable changes (it is the score returned from _compare_frames_change_detection()_). In the end, I decided to use a relatively large kernel size **15x15**, which applies high amount of blur. In terms of computation, it did not change the overall duration much compared to applying multiple small kernel sizes. However, it is also possible to apply small kernel sizes multiple times.

* **min_contour_area:** After setting the **gaussian_blur_kernel**, I checked what **cv2.contourArea(c)** returns for each detected contour. I tested by comparing very similar, slightly different, and very different images. Since the score is calculated by summing up contour areas, I tried to keep the score low to filter more images. So, I decided to set this parameter to **1000**. To filter fewer images, it can be lower to around 500, which will make it to be more sensitive to small changes between two images.

* **similarity_threshold:** After setting **gaussian_blur_kernel** and **min_contour_area_**, I simply checked how the score changes on image pairs. It directly returns **0** for very similar images, and rapitly increases for similar (almost duplicated) images. At the begining, I set this parameter to 2500 and applied over all dataset, and I thought there were still some similar images, so checked the calculated scores for those images and observed they were around 3000-4000. So, I decided to set this parameter to **5000**. To filter more, I think it can still be increased up to 7500, however to filter less, it can be decreased to 2500. I think this is a reasonable range for these parameters.

## 4. What you would suggest to implement to improve data collection of unique cases in future?

* For the implementation, the collected data is very large. I would suggest to implement a fast and simple frame extraction to pick best 1 or 2 images of each second, then implement the similarity test and remove non-essential ones.

* From the setup side, it is quite important to have several camera angles of the environment.

* I would also pay attention to the position and angle of cameras with respect to the lights in the area, because during daylight the collected data may look good. However, when it gets darker and lights are on, it may lower the quality of collected image due to some reflections, high brightness, etc. It is possible to mask that part of the image, but it would probably better to collect directly a high quality image set that requires less preprocessing steps such as masking, filtering, resizing etc.

## 5. Any other comments about your solution?

In my solution, I designed the algorithm and set the parameters to clean as many similar images as possible. I kept **gaussian_blur_kernel** and **min_contour_area** parameters high to lower the score calculated by the "compare_frames_change_detection" function. Considering the significant volume of data in real-world applications, simply just one camera capturing a footage for one day at 30 frames per second, we have 2592000 frames per day.

Therefore, I thought it is essential to filter as much as possible. For this use case, there were 1080 images initially, and with these input parameters, 712 images were removed.

# Thank you!

Thank you, Perception Team of Kopernikus Automotive, for providing my the opportunity to present my solution.

Onurcan Köken