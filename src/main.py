from cap import Cap
import cv2



CAP=Cap(cam_id=0,active_image_scale_factor=20,active_image_check_interval=0.5,active_image_max_color_diff=[40,40,40],color_match_pattern=[["#ad7866",20],["#ce9e8e",15],["#c49580",10],["#89654f",15],["#764443",10],["#d9aa6d",10]],max_pixel_group_dist=5,min_pixel_group_size=100,hand_image_scale_factor=3,hand_size_ratio=30/45,hand_height=45,ratio_detection_buffor=0.1,size_detection_buffor=10,max_hand_detection_time=10)
CAP.start()



while (CAP.cap.isOpened()):
	_,img=CAP.cap.read()
	cv2.imshow("Cam",img)
	cv2.imshow("Detection",CAP.d_img)
	if (cv2.waitKey(1)&0xff==27):
		break
CAP.end()
cv2.destroyAllWindows()
