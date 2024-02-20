from PIL import Image
import stapipy
from helper.config import CROPPED_IMAGE_WIDTH, CROPPED_IMAGE_HEIGHT

class Camera:

    def __init__(self):
        # Initialize StApi before using.
        stapipy.initialize()
        # Create a system object for device scan and connection.
        st_system = stapipy.create_system()
        # Connect to first detected device.
        self.st_device = st_system.create_first_device()

    def take_photo(self, file_path, file_path_high_resolution):
        st_device = self.st_device
        try:
            print('Device=', st_device.info.display_name)

            # Create a datastream object for handling image stream data.
            st_datastream = st_device.create_datastream()

            # Start the image acquisition of the host (local machine) side.
            st_datastream.start_acquisition(1)

            # Start the image acquisition of the camera side.
            st_device.acquisition_start()

            is_image_saved = False
                        
            with st_datastream.retrieve_buffer() as st_buffer:
                # Check if the acquired data contains image data.
                if st_buffer.info.is_image_present:
                    # Create an image object.
                    st_image = st_buffer.get_image()
                    # Display the information of the acquired image data.
                    print("BlockID={0} Size={1} x {2} First Byte={3}".format(
                        st_buffer.info.frame_id,
                        st_image.width, st_image.height,
                        st_image.get_image_data()[0]))

                    print("done.")
                    is_image_saved = True
                else:
                    # If the acquired data contains no image data.
                    print("Image data does not exist.")

            # Load StapiRaw and process the image.
            if is_image_saved:
                st_stillimage_filer = stapipy.create_filer(
                    stapipy.EStFilerType.StillImage)
                # Convert image to BGR8 format.
                st_converter = stapipy.create_converter(
                    stapipy.EStConverterType.PixelFormat)
                st_converter.destination_pixel_format = \
                    stapipy.EStPixelFormatNamingConvention.BGR8
                st_image = st_converter.convert(st_image)

                # Save as bitmap, tiff, png, jpg, csv
                file_format = stapipy.EStStillImageFileFormat.PNG
                
                print(f"Saving {file_path_high_resolution} ... ", end="")
                st_stillimage_filer.save(st_image, file_format, file_path_high_resolution)
                print("done.")
            print("Resizing")
            
            im = Image.open(file_path_high_resolution)
            print(im.size)
            image_width = 842
            image_height = 705
            img2 = im.resize((image_width, image_height))
            
            center_x = image_width/2
            center_y = image_height/2
            crop_x_half = int(CROPPED_IMAGE_WIDTH)/2
            crop_y_half = int(CROPPED_IMAGE_HEIGHT)/2
            box = (center_x - crop_x_half, center_y - crop_y_half, center_x + crop_x_half, center_y + crop_y_half )
            # print("Box ", box)

            new_size = img2.crop(box)

            new_size.save(file_path)
            # Stop the image acquisition of the camera side
            st_device.acquisition_stop()

            # Stop the image acquisition of the host side
            st_datastream.stop_acquisition()
            return file_path
        except Exception as exception:
            print(exception)

