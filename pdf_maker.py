from PIL import Image
import os

def order_pages(path_to_images):
    '''
    Why didn't I just use a library?!?
    Bubble sort for efficiency
    '''
    image_file_names = os.listdir(path_to_images)
    # add path to filename
    image_file_paths = [path_to_images + '/' + p for p in image_file_names]

    for path in image_file_paths:
        if path[-9:-4] == 'Cover':
            image_file_paths.remove(path)
            if path[-10] == 't':
                front_cover = path
            else:
                back_cover = path
    n = len(image_file_paths) 
    for i in range(0, n):
        for j in range(0, n - i - 1):
            j_page_number = int(image_file_paths[j][-8:-4])
            j_plus_one_page_number = int(image_file_paths[j + 1][-8:-4])
            if j_page_number > j_plus_one_page_number:
                image_file_paths[j], image_file_paths[j + 1] = image_file_paths[j + 1], image_file_paths[j]

    return image_file_paths, front_cover, back_cover 

def convert_to_pdf(ordered_filepath_list, front_cover, back_cover, pdf_path, pdf_name):
    images = []

    for fp in ordered_filepath_list:
        img = Image.open(fp)
        converted_img = img.convert('RGB')
        images.append(converted_img)

    fc = Image.open(front_cover)
    converted_front_cover = fc.convert('RGB')
    bc = Image.open(back_cover)
    converted_back_cover = bc.convert('RGB')
    images.append(converted_back_cover)

    converted_front_cover.save(pdf_path + '/' + pdf_name, save_all=True, append_images=images)
    return

def make_pdf(path_to_images, destination_path, name):
    ordered_filepath_list, front_cover, back_cover = order_pages(path_to_images)
    convert_to_pdf(ordered_filepath_list, front_cover, back_cover, destination_path, name)
    return

def main():
    path_to_images = input('Where are the images? Enter directory path: ')        
    destination_path = input('Where do you want the pdf? Enter directory path: ')
    name = input('Enter a filename for the pdf: ')
    make_pdf(path_to_images, destination_path, name)

if __name__=='__main__':
    main()