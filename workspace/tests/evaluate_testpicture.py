import sys
sys.path.append('.')
from old.gui import start_grid_vis
from classifier.predict import predict_image_list, write_predict_result, read_predict_result

# from camera.save_and_load_image import take_photos_helper
# Take photo from camera


output_images = ['storage/cam_photos/STC-MBS500U3V(22K5341)1_0.png', 'storage/cam_photos/STC-MBS500U3V(22K5341)1_1.png', 'storage/cam_photos/STC-MBS500U3V(22K5341)1_2.png', 'storage/cam_photos/STC-MBS500U3V(22K5341)1_3.png',
                 'storage/cam_photos/STC-MBS500U3V(22K5341)1_4.png', 'storage/cam_photos/STC-MBS500U3V(22K5341)1_5.png', 'storage/cam_photos/STC-MBS500U3V(22K5341)1_6.png', 'storage/cam_photos/STC-MBS500U3V(22K5341)1_7.png']

res = predict_image_list(output_images)
write_predict_result(res)
res_storage = read_predict_result()
print(res_storage)
#start_grid_vis(res_storage)
# Predict
# store prediction
# visualize in GUI
