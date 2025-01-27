# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

import sys
import torch
import cv2
from PIL import Image
import numpy as np
from sort import Sort
import time
import datetime



from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import pyqtSlot, QDate, QThread,pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap
import qimage2ndarray 



#=====================================================================
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
model = torch.hub.load('yolov5', 'custom', path='model/3best16.pt', source='local')  # local repo
#=====================================================================


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self, device):
        super().__init__()
        self._run_flag = True
        self.m = 0
        self.nm = 0
        self.wmi = 0
        self.c = 0
        self.device = device
    def convert_bbox_for_Sort(self, boxs):
        # raw box (dataframe) 
        boxs = boxs.to_numpy()
        bboxs = np.zeros((len(boxs), 5))
        bboxs[...,0] = boxs[..., 0]
        bboxs[...,1] = boxs[..., 1] 
        bboxs[...,2] = boxs[..., 2] 
        bboxs[...,3] = boxs[..., 3] 
        bboxs[...,4] = boxs[...,5]
        return bboxs 

    def run(self):
        mot_tracker = Sort(max_age=10, iou_threshold = 0.4, min_hits = 3)
        id_cls = {}
        cam = cv2.VideoCapture(self.device)
        if not cam.isOpened():
            print('Could not open video')
            sys.exit()
        while self._run_flag:
            ret, img = cam.read()
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            boxs = model(img).pandas().xyxy[0]
            detections = self.convert_bbox_for_Sort(boxs)
            track_bbs_ids = mot_tracker.update(detections)
            for i in range(len(track_bbs_ids)):
                box = track_bbs_ids[i]
                xmin = int(box[0])
                ymin = int(box[1])
                xmax = int(box[2])
                ymax = int(box[3])
                id_ = int(box[4])
                cls_ = int(box[5])

                id_cls[id_] = cls_
                v,c = np.unique(list(id_cls.values()), return_counts = True)
                count = dict(np.concatenate((v.reshape(-1,1),c.reshape(-1,1)), axis = 1))
                print(count)


                self.m, self.nm, self.wmi =0 ,0, 0
                self.c = len(count)
                if 1 in count:
                    self.m = count[1]
                if 0 in count:
                    self.nm = count[0]
                if 2 in count:
                    self.wmi = count[2]

                # img = cv2.putText(img,text = f'with_mask: {self.m}', 
                #     org = (0,30),fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=1, color=(20,255,3), thickness=2)
                # img = cv2.putText(img,text = f'without_mask:{self.nm}', 
                #     org = (0,60),fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=1, color=(2,28,255), thickness=2)
                # img = cv2.putText(img,text = f'mask_weared_incorrect:{self.wmi}', 
                #     org = (0,90),fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=1, color=(3,255,255), thickness=2)
                img = cv2.putText(img, text=f' id:{id_}', org=(
                    xmin, ymin), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(128, 0, 0), thickness=2)
                if cls_ == 0:
                    img = cv2.rectangle(img, pt1=(xmin, ymin), pt2=(
                        xmax, ymax), color=(255,0,0), thickness=2)
                elif cls_ ==1:
                    img = cv2.rectangle(img, pt1=(xmin, ymin), pt2=(
                        xmax, ymax), color=(4, 179, 0), thickness=2)
                else:
                    img = cv2.rectangle(img, pt1=(xmin, ymin), pt2=(
                        xmax, ymax), color=(255, 250, 9), thickness=2)

            self.change_pixmap_signal.emit(img)
        cap.release()
    def stop(self):
        self._run_flag = False
        self.wait()



class Ui_MainWindow(QDialog):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(965, 600)

        # tao luong xu ly hinh anh 
        self.runThread = False
        
        

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 490, 681, 80))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.btnCancel = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btnCancel.setObjectName("btnCancel")
        self.gridLayout.addWidget(self.btnCancel, 0, 2, 1, 1)
        self.btnChoice = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btnChoice.setObjectName("btnChoice")
        self.gridLayout.addWidget(self.btnChoice, 0, 0, 1, 1)
        self.btnWepcam = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btnWepcam.setObjectName("btnWepcam")
        self.gridLayout.addWidget(self.btnWepcam, 0, 1, 1, 1)
        self.gridLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(690, 20, 261, 80))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lbl_date1 = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.lbl_date1.setObjectName("lbl_date1")
        self.horizontalLayout.addWidget(self.lbl_date1)
        self.lbl_date2 = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.lbl_date2.setObjectName("lbl_date2")
        self.horizontalLayout.addWidget(self.lbl_date2)
        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lbl_time1 = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.lbl_time1.setObjectName("lbl_time1")
        self.horizontalLayout_2.addWidget(self.lbl_time1)
        self.lbl_time2 = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.lbl_time2.setObjectName("lbl_time2")
        self.horizontalLayout_2.addWidget(self.lbl_time2)
        self.gridLayout_2.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(690, 140, 261, 421))
        self.groupBox.setObjectName("groupBox")
        self.gridLayoutWidget_3 = QtWidgets.QWidget(self.groupBox)
        self.gridLayoutWidget_3.setGeometry(QtCore.QRect(10, 40, 241, 371))
        self.gridLayoutWidget_3.setObjectName("gridLayoutWidget_3")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.gridLayoutWidget_3)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.lbl_mask1 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        self.lbl_mask1.setObjectName("lbl_mask1")
        self.horizontalLayout_3.addWidget(self.lbl_mask1)
        self.lbl_mask2 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        self.lbl_mask2.setObjectName("lbl_mask2")
        self.horizontalLayout_3.addWidget(self.lbl_mask2)
        self.gridLayout_3.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.lbl_incorrect1 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        self.lbl_incorrect1.setObjectName("lbl_incorrect1")
        self.horizontalLayout_5.addWidget(self.lbl_incorrect1)
        self.lbl_incorrect2 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        self.lbl_incorrect2.setObjectName("lbl_incorrect2")
        self.horizontalLayout_5.addWidget(self.lbl_incorrect2)
        self.gridLayout_3.addLayout(self.horizontalLayout_5, 2, 0, 1, 1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.lbl_nomask1 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        self.lbl_nomask1.setObjectName("lbl_nomask1")
        self.horizontalLayout_4.addWidget(self.lbl_nomask1)
        self.lbl_nomask2 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        self.lbl_nomask2.setObjectName("lbl_nomask2")
        self.horizontalLayout_4.addWidget(self.lbl_nomask2)
        self.gridLayout_3.addLayout(self.horizontalLayout_4, 1, 0, 1, 1)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label = QtWidgets.QLabel(self.gridLayoutWidget_3)
        self.label.setObjectName("label")
        self.horizontalLayout_6.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_6.addWidget(self.label_2)
        self.gridLayout_3.addLayout(self.horizontalLayout_6, 3, 0, 1, 1)
        self.lbl_Image = QtWidgets.QLabel(self.centralwidget)
        self.lbl_Image.setGeometry(QtCore.QRect(6, 26, 671, 441))
        self.lbl_Image.setText("")
        self.lbl_Image.setObjectName("lbl_Image")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):

        #update time and date 
        now_ = QDate.currentDate()
        current_date = now_.toString('dd MMMM yyyy')
        current_time = datetime.datetime.now().strftime('%I:%H %p')


        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btnCancel.setText(_translate("MainWindow", "Cancel"))
        self.btnCancel.clicked.connect(sys.exit)
        self.btnChoice.setText(_translate("MainWindow", "Choice file ..."))
        self.btnChoice.clicked.connect(self.btnChoiceEvent)
        self.btnWepcam.setText(_translate("MainWindow", " Start with Webcam"))
        self.btnWepcam.clicked.connect(self.btnWepcamEvent)
        self.lbl_date1.setText(_translate("MainWindow", "Date: "))
        self.lbl_date2.setText(_translate("MainWindow", current_date))
        self.lbl_time1.setText(_translate("MainWindow", "Time: "))
        self.lbl_time2.setText(_translate("MainWindow", current_time))
        self.groupBox.setTitle(_translate("MainWindow", "Detail"))
        self.lbl_mask1.setText(_translate("MainWindow", "Mask:"))
        self.lbl_mask2.setText(_translate("MainWindow", "0"))
        self.lbl_incorrect1.setText(_translate("MainWindow", "Incorrect:"))
        self.lbl_incorrect2.setText(_translate("MainWindow", "0"))
        self.lbl_nomask1.setText(_translate("MainWindow", "No_mask: "))
        self.lbl_nomask2.setText(_translate("MainWindow", "0"))
        self.label.setText(_translate("MainWindow", "Total: "))
        self.label_2.setText(_translate("MainWindow", "0"))




    def btnChoiceEvent(self):
        filepath = QtWidgets.QFileDialog.getOpenFileName(self, 'Hey! Select a File')

        self.thread = VideoThread(filepath[0])
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()


    
    def btnWepcamEvent(self):
        print(self.runThread)
        if self.runThread:
            self.runThread = False
            self.thread.change_pixmap_signal.disconnect()
            self.btnWepcam.setText('Continue....')

        else:
            self.runThread = True
            self.thread = VideoThread(0)
            self.thread.change_pixmap_signal.connect(self.update_image)
            self.thread.start()
            self.btnWepcam.setText('Stop')
            
 



    @pyqtSlot(np.ndarray)
    def update_image(self,cv_img):
        qt_img = self.convert_cv_qt(cv_img)
        self.lbl_Image.setPixmap(qt_img)
        self.lbl_mask2.setText(str(self.thread.m))
        self.lbl_nomask2.setText(str(self.thread.nm))
        self.lbl_incorrect2.setText(str(self.thread.wmi))
        self.label_2.setText(str(self.thread.c))

    def convert_cv_qt(self, cv_img):
        h,w,ch = cv_img.shape
        bytes_per_line = ch*w
        Qt_format = QtGui.QImage(cv_img.data, w , h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = Qt_format.scaled(self.lbl_Image.width(), self.lbl_Image.height(), Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
        
    

        








if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = Ui_MainWindow()
    w = QtWidgets.QMainWindow()
    ex.setupUi(w)
    w.show()
    sys.exit(app.exec_())