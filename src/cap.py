from PIL import Image, ImageDraw
import cv2
import numpy
import threading
import time



class Cap:
	def __init__(self,**opts):
		self.opts={"cam_id":0,"active_image_scale_factor":1,"active_image_check_interval":0,"active_image_max_color_diff":[10,10,10],"color_match_pattern":[["#ff0000",20]],"max_pixel_group_dist":10,"min_pixel_group_size":50,"hand_image_scale_factor":1,"hand_size_ratio":1/2,"hand_height":30,"ratio_detection_buffor":0.02,"size_detection_buffor":15,"max_hand_detection_time":10,"good_detect_callback":lambda:print("Detected!"),"bad_detect_callback":lambda:print("Nothing")}
		self.opts.update(opts)
		self.state=0
		self.cap=cv2.VideoCapture(self.opts["cam_id"])
		self.size=self.calc_size()
		self.d_img=self.null_img()
		self._end=False
		self.last_img=None
		self.opts["color_match_pattern"]=self.conv_c(self.opts["color_match_pattern"])



	def start(self):
		thr=threading.Thread(target=self.loop,args=(),kwargs={})
		thr.deamon=True
		thr.start()
	def end(self):
		self.cap.release()
		self._end=True



	def conv_c(self,cl):
		color=[]
		for c in cl:
			color.append([int(c[0][1:3],16),int(c[0][3:5],16),int(c[0][5:7],16),c[1],c[2] if (len(c)>2) else c[1],c[3] if (len(c)>3) else c[1]])
		return color



	def loop(self):
		while True:
			while True:
				self.d_img,self.state=self.process_cap_active()
				if (self.state!=0):
					break
				if (self._end==True):
					return
				time.sleep(self.opts["active_image_check_interval"])
			s=time.time()
			while True:
				self.d_img,self.state=self.process_cap_hand()
				if (self.state==2 or time.time()-s>self.opts["max_hand_detection_time"]):
					break
				if (self._end==True):
					return
			if (self.state==2):
				self.opts["good_detect_callback"]()
			else:
				self.opts["bad_detect_callback"]()
			while True:
				self.d_img,self.state=self.process_cap_active()
				if (self.state==0):
					break
				if (self._end==True):
					return
				time.sleep(self.opts["active_image_check_interval"])



	def calc_size(self):
		_,img=self.cap.read()
		return (img.shape[1],img.shape[0])
	def null_img(self):
		return cv2.cvtColor(numpy.array(Image.new("RGB",self.size)),cv2.COLOR_RGB2BGR)



	def process_cap_hand(self):
		_,img=self.cap.read()
		if (type(img)!=numpy.ndarray):
			return [],0
		h,w,_=img.shape
		img=cv2.resize(img,(w//self.opts["hand_image_scale_factor"],h//self.opts["hand_image_scale_factor"]))
		img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
		img=Image.fromarray(img)
		data=list(img.getdata())
		groups=[]
		x,y=0,0
		for i in range(0,len(data)):
			s=False
			for cl in self.opts["color_match_pattern"]:
				if (abs(data[i][0]-cl[0])<=cl[3] and abs(data[i][1]-cl[1])<=cl[4] and abs(data[i][2]-cl[2])<=cl[5]):
					s=True
					break
			if (s==True):
				if (len(groups)==0):
					groups.append([[i,x,y]])
				else:
					s=False
					for g in groups:
						for e in g:
							if (abs(e[1]-x)+abs(e[2]-y)<=self.opts["max_pixel_group_dist"]):
								s=True
								break
						if (s==True):
							g.append([i,x,y])
							break
					if (s==False):
						groups.append([[i,x,y]])
			x+=1
			if (x>=img.width):
				x=0
				y+=1
		mg=None
		bl=-1
		for g in groups:
			if (len(g)>bl):
				bl=len(g)
				mg=g
		img=Image.new("RGB",(img.width,img.height))
		if (mg==None or len(mg)<self.opts["min_pixel_group_size"]):
			img=cv2.cvtColor(numpy.array(img),cv2.COLOR_RGB2BGR)
			h,w,_=img.shape
			img=cv2.resize(img,(w*self.opts["hand_image_scale_factor"],h*self.opts["hand_image_scale_factor"]))
			return img,0
		a,b=[img.width,img.height],[0,0]
		for e in mg:
			a=[min(a[0],e[1]),min(a[1],e[2])]
			b=[max(b[0],e[1]),max(b[1],e[2])]
			img.putpixel((e[1:3]),(255,)*3)
		state=False
		if (abs((b[0]-a[0])/(b[1]-a[1])-self.opts["hand_size_ratio"])<=self.opts["ratio_detection_buffor"] and abs((b[1]-a[1])-self.opts["hand_height"])<=self.opts["size_detection_buffor"]):
			state=True
		draw=ImageDraw.Draw(img)
		if (state==True):
			draw.rectangle(((a[0],a[1]),(b[0],b[1])),outline="lime")
		else:
			draw.rectangle(((a[0],a[1]),(b[0],b[1])),outline="red")
		img=cv2.cvtColor(numpy.array(img),cv2.COLOR_RGB2BGR)
		h,w,_=img.shape
		img=cv2.resize(img,(w*self.opts["hand_image_scale_factor"],h*self.opts["hand_image_scale_factor"]))
		return img,(2 if state==True else 1)
	def process_cap_active(self):
		_,img=self.cap.read()
		if (type(img)!=numpy.ndarray):
			return [],0
		h,w,_=img.shape
		r_img=cv2.resize(img,(w//self.opts["active_image_scale_factor"],h//self.opts["active_image_scale_factor"]))
		img=cv2.cvtColor(r_img,cv2.COLOR_BGR2RGB)
		img=Image.fromarray(img)
		r_img=cv2.resize(r_img,(w,h))
		data=list(img.getdata())
		if (self.last_img==None):
			self.last_img=img
			return r_img,0
		l_data=list(self.last_img.getdata())
		self.last_img=img
		for i in range(0,len(data)):
			c1=data[i]
			c2=l_data[i]
			if (abs(c1[0]-c2[0])>self.opts["active_image_max_color_diff"][0] or abs(c1[1]-c2[1])>self.opts["active_image_max_color_diff"][1] or abs(c1[2]-c2[2])>self.opts["active_image_max_color_diff"][2]):
				return r_img,-1
		return r_img,0



if (__name__=="__main__"):
	CAP=Cap(cam_id=1,active_image_scale_factor=10,active_image_check_interval=0.5,active_image_max_color_diff=[40,40,40],color_match_pattern=[["#ad7866",20],["#ce9e8e",15],["#c49580",10],["#89654f",15],["#764443",10],["#d9aa6d",10]],max_pixel_group_dist=5,min_pixel_group_size=100,hand_image_scale_factor=3,hand_size_ratio=30/45,hand_height=45,ratio_detection_buffor=0.1,size_detection_buffor=10,max_hand_detection_time=10)
	CAP.start()
	while True:
		_,img=CAP.cap.read()
		cv2.imshow("Cam",img)
		cv2.imshow("Detection",CAP.d_img)
		if (cv2.waitKey(30)&0xff==27):
			break
	CAP.end()
	cv2.destroyAllWindows()
