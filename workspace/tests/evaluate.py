from helper.camera import take_photos_helper
from classifier.predict import predict_image_list,  verify_predcit, write_predict_result, read_predict_result

from old.gui import start_grid_vis, start_grid_vis_val


def verify():
    pred_state, rel_state = verify_predcit()
    start_grid_vis_val(pred_state, rel_state)


def run():
    # output_images = ["classifier/testdataset/2208241448352.png"]
    output_images = take_photos_helper(8)
    res = predict_image_list(output_images)
    write_predict_result(res)
    res_storage = read_predict_result()
    start_grid_vis(res_storage)


# Uncomment this line to capture camrea photos and run (Show gui with only predicted values)
run()

# Uncomment this line to verify on CSV (Show real and predicted values)
# verify()
