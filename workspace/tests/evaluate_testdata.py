import sys
sys.path.append('.')
from old.gui import start_grid_vis_val, start_grid_vis
from classifier.predict import predict_image_list, write_predict_result, read_predict_result

# from camera.save_and_load_image import take_photos_helper
# Take photo from camera

# output_images = take_photos_helper(8)
output_images = ["classifier/testdataset/2208241448352.png",
                 "classifier/testdataset/2208241451044.png",
                 "classifier/testdataset/2208241549186.png",
                 "classifier/testdataset/2208241626487.png",
                 "classifier/testdataset/2208241639537.png",
                 "classifier/testdataset/2208241719481.png",
                 "classifier/testdataset/2208241801334.png",
                 "classifier/testdataset/2208241815522.png",
                 ]
res = predict_image_list(output_images)
write_predict_result(res)
res_storage = read_predict_result()
start_grid_vis(res_storage)
# start_grid_vis_val(res_storage)
# Predict
# store prediction
# visualize in GUI
